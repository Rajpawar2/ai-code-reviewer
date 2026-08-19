from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class FindingBase(BaseModel):
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    category: str  # "bug", "security", "performance", "quality", "maintainability", "ast", "lint", "complexity"
    title: str
    description: str
    line_number: int = 0
    recommendation: Optional[str] = None
    suggested_code: Optional[str] = None


class FindingResponse(FindingBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    review_id: str
    created_at: datetime


class ReviewCreateRequest(BaseModel):
    filename: Optional[str] = Field(default="code_snippet.py", max_length=255)
    source_code: str = Field(..., min_length=1, max_length=500000)
    project_id: Optional[str] = None
    source_type: Optional[str] = "snippet"


class ReviewFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    language: str
    lines_of_code: int
    complexity: str
    created_at: datetime


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    project_id: Optional[str] = None
    source_type: str
    filename: str
    source_code: str
    overall_score: float
    security_score: float
    quality_score: float
    performance_score: float
    maintainability_score: float
    ai_available: bool
    ai_summary: Optional[str] = None
    fixed_code: Optional[str] = None
    created_at: datetime
    findings: List[FindingResponse] = []
    files: List[ReviewFileResponse] = []


class ReviewSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    filename: str
    source_type: str
    overall_score: float
    security_score: float
    quality_score: float
    performance_score: float
    maintainability_score: float
    ai_available: bool
    findings_count: int
    created_at: datetime


class DashboardStatsResponse(BaseModel):
    total_reviews: int
    average_score: float
    critical_issues_count: int
    security_issues_count: int
    quality_avg: float
    security_avg: float
    performance_avg: float
    maintainability_avg: float
    recent_reviews: List[ReviewSummaryResponse]
