import re
import io
import zipfile
import httpx
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.schemas.github import GitHubAnalyzeRequest, GitHubAnalysisResponse, FileAnalysisResult
from app.schemas.review import FindingBase
from app.services.analysis_service import AnalysisService
from app.database.models import Review, Finding, ReviewFile


class GitHubService:
    """Safely retrieves and analyzes Python files from GitHub repositories without code execution."""

    IGNORED_DIRS = {
        ".git", "node_modules", "venv", ".venv", "env", "__pycache__",
        "dist", "build", ".idea", ".vscode", "site-packages"
    }

    def __init__(self, db: Session, analysis_service: Optional[AnalysisService] = None):
        self.db = db
        self.analysis_service = analysis_service or AnalysisService()

    @staticmethod
    def validate_github_url(url: str) -> bool:
        pattern = r"^https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$"
        return bool(re.match(pattern, url.strip()))

    @staticmethod
    def parse_repo_info(url: str) -> Dict[str, str]:
        url = url.strip().rstrip("/")
        parts = url.split("/")
        return {
            "owner": parts[-2],
            "repo": parts[-1].removesuffix(".git"),
            "full_name": f"{parts[-2]}/{parts[-1].removesuffix('.git')}"
        }

    async def analyze_repository(
        self,
        user_id: str,
        request: GitHubAnalyzeRequest
    ) -> GitHubAnalysisResponse:
        url = request.repository_url.strip()
        if not self.validate_github_url(url):
            raise ValueError("Invalid GitHub repository URL. Must be in format: https://github.com/owner/repository")

        repo_info = self.parse_repo_info(url)
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        repo_name = repo_info["full_name"]

        logger.info(f"Fetching GitHub repository for analysis: {repo_name}")

        # Fetch zip archive of the default branch
        zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "AI-Code-Reviewer"}
        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

        python_files: Dict[str, str] = {}
        total_size = 0

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            res = await client.get(zip_url, headers=headers)
            if res.status_code == 404:
                raise ValueError(f"GitHub repository '{repo_name}' not found or is private.")
            elif res.status_code != 200:
                raise ValueError(f"Failed to fetch repository from GitHub: HTTP {res.status_code}")

            # Read zip in-memory
            try:
                with zipfile.ZipFile(io.BytesIO(res.content)) as zf:
                    for zip_info in zf.infolist():
                        if zip_info.is_dir():
                            continue
                        
                        # Strip root folder (e.g. owner-repo-hash/)
                        parts = zip_info.filename.split("/", 1)
                        rel_path = parts[1] if len(parts) > 1 else parts[0]

                        # Check ignored directories
                        path_parts = rel_path.split("/")
                        if any(p in self.IGNORED_DIRS for p in path_parts):
                            continue

                        # Only analyze .py files
                        if not rel_path.endswith(".py"):
                            continue

                        # Check single file size limit
                        if zip_info.file_size > (settings.MAX_SINGLE_FILE_SIZE_KB * 1024):
                            continue

                        total_size += zip_info.file_size
                        if total_size > (settings.MAX_REPO_TOTAL_SIZE_KB * 1024):
                            break

                        if len(python_files) >= settings.MAX_REPO_FILES:
                            break

                        try:
                            content = zf.read(zip_info).decode("utf-8")
                            python_files[rel_path] = content
                        except UnicodeDecodeError:
                            continue  # Skip binary/non-utf8 files
            except Exception as e:
                raise ValueError(f"Error processing repository archive: {str(e)}")

        if not python_files:
            raise ValueError(f"No valid Python source files found in repository '{repo_name}'.")

        logger.info(f"Found {len(python_files)} Python files in {repo_name}. Running analysis pipeline...")

        # Analyze each file
        file_results: List[FileAnalysisResult] = []
        all_findings: List[Dict[str, Any]] = []
        total_loc = 0
        total_score_sum = 0.0

        for file_path, code in python_files.items():
            analysis = await self.analysis_service.analyze_code(code, file_path)
            scores = analysis["scores"]
            complexity = analysis["complexity"]
            findings = analysis["findings"]

            total_loc += complexity.get("lines_of_code", 0)
            total_score_sum += scores["overall_score"]

            file_findings_schemas = []
            for f in findings:
                file_findings_schemas.append(
                    FindingBase(
                        severity=f.get("severity", "MEDIUM"),
                        category=f.get("category", "quality"),
                        title=f.get("title", "Issue"),
                        description=f.get("description", ""),
                        line_number=f.get("line_number", 0),
                        recommendation=f.get("recommendation"),
                        suggested_code=f.get("suggested_code")
                    )
                )
                all_findings.append({**f, "file_path": file_path})

            file_results.append(
                FileAnalysisResult(
                    filename=file_path,
                    lines_of_code=complexity.get("lines_of_code", 0),
                    complexity=complexity.get("complexity_level", "LOW"),
                    overall_score=scores["overall_score"],
                    findings=file_findings_schemas
                )
            )

        # Aggregate metrics
        avg_score = round(total_score_sum / len(file_results), 1)
        critical_count = sum(1 for f in all_findings if f.get("severity") == "CRITICAL")
        high_count = sum(1 for f in all_findings if f.get("severity") == "HIGH")
        security_count = sum(1 for f in all_findings if f.get("category") == "security")

        # Top problematic files (lowest score first)
        sorted_files = sorted(file_results, key=lambda x: x.overall_score)
        top_problematic = sorted_files[:5]

        # Determine average complexity
        if critical_count > 3 or any(f.complexity == "CRITICAL" for f in file_results):
            avg_complexity = "HIGH"
        elif any(f.complexity in ("HIGH", "MEDIUM") for f in file_results):
            avg_complexity = "MEDIUM"
        else:
            avg_complexity = "LOW"

        # Save repository review record in database
        review = Review(
            user_id=user_id,
            project_id=request.project_id,
            source_type="github_repo",
            filename=repo_name,
            source_code=f"GitHub Repository: {url}\nAnalyzed {len(file_results)} Python files ({total_loc} LOC).",
            overall_score=avg_score,
            security_score=max(0.0, 100.0 - (security_count * 10)),
            quality_score=avg_score,
            performance_score=avg_score,
            maintainability_score=avg_score,
            ai_available=True,
            ai_summary=f"Analyzed {len(file_results)} Python files from GitHub repo {repo_name}. Found {len(all_findings)} total findings across static & AI engines."
        )
        self.db.add(review)
        self.db.flush()

        for f in all_findings:
            finding_db = Finding(
                review_id=review.id,
                severity=f.get("severity", "MEDIUM"),
                category=f.get("category", "quality"),
                title=f"[{f.get('file_path')}] {f.get('title')}",
                description=f.get("description", ""),
                line_number=f.get("line_number", 0),
                recommendation=f.get("recommendation"),
                suggested_code=f.get("suggested_code")
            )
            self.db.add(finding_db)

        for fr in file_results:
            rf = ReviewFile(
                review_id=review.id,
                filename=fr.filename,
                language="python",
                lines_of_code=fr.lines_of_code,
                complexity=fr.complexity
            )
            self.db.add(rf)

        self.db.commit()

        return GitHubAnalysisResponse(
            repository_name=repo_name,
            repository_url=url,
            review_id=review.id,
            total_files_analyzed=len(file_results),
            repository_score=avg_score,
            total_findings=len(all_findings),
            critical_issues_count=critical_count,
            high_issues_count=high_count,
            security_issues_count=security_count,
            average_complexity=avg_complexity,
            top_problematic_files=top_problematic,
            all_files=file_results
        )
