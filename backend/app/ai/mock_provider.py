from typing import Dict, Any, List
from app.ai.base import AIProvider, AIReviewResult, AIIssueItem


class MockAIProvider(AIProvider):
    """Deterministic Mock AI Provider for automated tests and offline simulation."""

    async def review_code(
        self,
        code: str,
        filename: str,
        static_findings: List[Dict[str, Any]],
        complexity: Dict[str, Any]
    ) -> AIReviewResult:
        bugs: List[AIIssueItem] = []
        security_issues: List[AIIssueItem] = []
        performance_issues: List[AIIssueItem] = []
        code_quality_issues: List[AIIssueItem] = []
        best_practices: List[AIIssueItem] = []

        # Convert static findings into AI structured issues
        for f in static_findings:
            cat = f.get("category", "quality")
            item = AIIssueItem(
                severity=f.get("severity", "MEDIUM"),
                title=f.get("title", "Detected Issue"),
                description=f.get("description", "Code issue detected by static analyzer"),
                line_number=f.get("line_number", 1),
                recommendation=f.get("recommendation", "Apply refactoring recommendation"),
                suggested_code=f.get("suggested_code")
            )
            if cat in ("bug", "ast"):
                bugs.append(item)
            elif cat == "security":
                security_issues.append(item)
            elif cat == "performance":
                performance_issues.append(item)
            elif cat in ("complexity", "maintainability"):
                code_quality_issues.append(item)
            else:
                best_practices.append(item)

        summary = (
            f"Mock AI Code Review for '{filename}'. Found {len(static_findings)} issues across "
            f"AST, Ruff, Bandit, and Radon analyzers. Maintainability index: {complexity.get('maintainability_index', 100)}."
        )

        fixed_code = f"# AI-Optimized and Refactored Version of {filename}\n" + code

        return AIReviewResult(
            summary=summary,
            bugs=bugs,
            security_issues=security_issues,
            performance_issues=performance_issues,
            code_quality_issues=code_quality_issues,
            best_practices=best_practices,
            fixed_code=fixed_code
        )

    async def check_health(self) -> Dict[str, Any]:
        return {
            "available": True,
            "provider": "mock",
            "model": "mock-qwen2.5-coder",
            "message": "Mock AI provider is operational."
        }
