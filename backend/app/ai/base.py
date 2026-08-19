from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AIIssueItem(BaseModel):
    severity: str = "MEDIUM"
    title: str
    description: str
    line_number: int = 0
    recommendation: str = ""
    suggested_code: Optional[str] = None


class AIReviewResult(BaseModel):
    summary: str
    bugs: List[AIIssueItem] = Field(default_factory=list)
    security_issues: List[AIIssueItem] = Field(default_factory=list)
    performance_issues: List[AIIssueItem] = Field(default_factory=list)
    code_quality_issues: List[AIIssueItem] = Field(default_factory=list)
    best_practices: List[AIIssueItem] = Field(default_factory=list)
    fixed_code: Optional[str] = None


class AIProvider(ABC):
    @abstractmethod
    async def review_code(
        self,
        code: str,
        filename: str,
        static_findings: List[Dict[str, Any]],
        complexity: Dict[str, Any]
    ) -> AIReviewResult:
        """Analyze code using LLM or Mock Provider with static findings and complexity as context."""
        pass

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """Check availability of the AI provider service."""
        pass
