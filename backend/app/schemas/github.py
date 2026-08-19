from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.review import FindingBase


class GitHubAnalyzeRequest(BaseModel):
    repository_url: str = Field(..., description="GitHub repository HTTPS URL")
    project_id: Optional[str] = None


class FileAnalysisResult(BaseModel):
    filename: str
    lines_of_code: int
    complexity: str
    overall_score: float
    findings: List[FindingBase]


class GitHubAnalysisResponse(BaseModel):
    repository_name: str
    repository_url: str
    review_id: str
    total_files_analyzed: int
    repository_score: float
    total_findings: int
    critical_issues_count: int
    high_issues_count: int
    security_issues_count: int
    average_complexity: str
    top_problematic_files: List[FileAnalysisResult]
    all_files: List[FileAnalysisResult]
