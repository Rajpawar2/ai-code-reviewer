from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database.models import Review, Finding, ReviewFile
from app.schemas.review import ReviewCreateRequest, DashboardStatsResponse, ReviewSummaryResponse
from app.services.analysis_service import AnalysisService


class ReviewService:
    """Manages database storage, user access scoping, and retrieval of Code Reviews."""

    def __init__(self, db: Session, analysis_service: Optional[AnalysisService] = None):
        self.db = db
        self.analysis_service = analysis_service or AnalysisService()

    async def create_review(
        self,
        user_id: str,
        request: ReviewCreateRequest
    ) -> Review:
        # Run full analysis
        result = await self.analysis_service.analyze_code(
            code=request.source_code,
            filename=request.filename or "code_snippet.py"
        )

        scores = result["scores"]
        complexity = result["complexity"]

        review = Review(
            user_id=user_id,
            project_id=request.project_id,
            source_type=request.source_type or "snippet",
            filename=request.filename or "code_snippet.py",
            source_code=request.source_code,
            overall_score=scores["overall_score"],
            security_score=scores["security_score"],
            quality_score=scores["quality_score"],
            performance_score=scores["performance_score"],
            maintainability_score=scores["maintainability_score"],
            ai_available=result["ai_available"],
            ai_summary=result.get("ai_summary"),
            fixed_code=result.get("fixed_code")
        )
        self.db.add(review)
        self.db.flush()

        # Add findings
        for f in result.get("findings", []):
            finding = Finding(
                review_id=review.id,
                severity=f.get("severity", "MEDIUM"),
                category=f.get("category", "quality"),
                title=f.get("title", "Issue"),
                description=f.get("description", ""),
                line_number=f.get("line_number", 0),
                recommendation=f.get("recommendation"),
                suggested_code=f.get("suggested_code")
            )
            self.db.add(finding)

        # Add review file entry
        review_file = ReviewFile(
            review_id=review.id,
            filename=request.filename or "code_snippet.py",
            language="python",
            lines_of_code=complexity.get("lines_of_code", 0),
            complexity=complexity.get("complexity_level", "LOW")
        )
        self.db.add(review_file)

        self.db.commit()
        self.db.refresh(review)
        return review

    def get_user_reviews(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Review]:
        return (
            self.db.query(Review)
            .filter(Review.user_id == user_id)
            .order_by(desc(Review.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_review_by_id(self, review_id: str, user_id: str) -> Optional[Review]:
        return (
            self.db.query(Review)
            .filter(Review.id == review_id, Review.user_id == user_id)
            .first()
        )

    def delete_review(self, review_id: str, user_id: str) -> bool:
        review = self.get_review_by_id(review_id, user_id)
        if not review:
            return False
        self.db.delete(review)
        self.db.commit()
        return True

    def get_dashboard_stats(self, user_id: str) -> DashboardStatsResponse:
        reviews = (
            self.db.query(Review)
            .filter(Review.user_id == user_id)
            .order_by(desc(Review.created_at))
            .all()
        )

        total_reviews = len(reviews)
        if total_reviews == 0:
            return DashboardStatsResponse(
                total_reviews=0,
                average_score=100.0,
                critical_issues_count=0,
                security_issues_count=0,
                quality_avg=100.0,
                security_avg=100.0,
                performance_avg=100.0,
                maintainability_avg=100.0,
                recent_reviews=[]
            )

        avg_score = round(sum(r.overall_score for r in reviews) / total_reviews, 1)
        quality_avg = round(sum(r.quality_score for r in reviews) / total_reviews, 1)
        security_avg = round(sum(r.security_score for r in reviews) / total_reviews, 1)
        performance_avg = round(sum(r.performance_score for r in reviews) / total_reviews, 1)
        maint_avg = round(sum(r.maintainability_score for r in reviews) / total_reviews, 1)

        # Count critical and security findings
        critical_count = (
            self.db.query(func.count(Finding.id))
            .join(Review, Finding.review_id == Review.id)
            .filter(Review.user_id == user_id, Finding.severity == "CRITICAL")
            .scalar() or 0
        )

        security_count = (
            self.db.query(func.count(Finding.id))
            .join(Review, Finding.review_id == Review.id)
            .filter(Review.user_id == user_id, Finding.category == "security")
            .scalar() or 0
        )

        recent_summaries = []
        for r in reviews[:10]:
            findings_count = len(r.findings)
            recent_summaries.append(
                ReviewSummaryResponse(
                    id=r.id,
                    user_id=r.user_id,
                    filename=r.filename,
                    source_type=r.source_type,
                    overall_score=r.overall_score,
                    security_score=r.security_score,
                    quality_score=r.quality_score,
                    performance_score=r.performance_score,
                    maintainability_score=r.maintainability_score,
                    ai_available=r.ai_available,
                    findings_count=findings_count,
                    created_at=r.created_at
                )
            )

        return DashboardStatsResponse(
            total_reviews=total_reviews,
            average_score=avg_score,
            critical_issues_count=critical_count,
            security_issues_count=security_count,
            quality_avg=quality_avg,
            security_avg=security_avg,
            performance_avg=performance_avg,
            maintainability_avg=maint_avg,
            recent_reviews=recent_summaries
        )
