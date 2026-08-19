from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.api.auth import get_current_user
from app.schemas.review import (
    ReviewCreateRequest,
    ReviewResponse,
    ReviewSummaryResponse,
    DashboardStatsResponse
)
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review_json(
    request: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not request.source_code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")
    if len(request.source_code) > 500000:
        raise HTTPException(status_code=413, detail="Source code exceeds maximum allowed size (500KB).")

    service = ReviewService(db)
    review = await service.create_review(current_user.id, request)
    return review


@router.post("/upload", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_review_file(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".py"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Python files (.py) are supported for code review."
        )

    content_bytes = await file.read()
    if len(content_bytes) > 500000:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum allowed limit (500KB)."
        )

    try:
        source_code = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not valid UTF-8 encoded text."
        )

    if not source_code.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    request = ReviewCreateRequest(
        filename=file.filename,
        source_code=source_code,
        project_id=project_id,
        source_type="file_upload"
    )
    service = ReviewService(db)
    review = await service.create_review(current_user.id, request)
    return review


@router.get("", response_model=List[ReviewSummaryResponse])
def get_user_reviews(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ReviewService(db)
    reviews = service.get_user_reviews(current_user.id, limit=limit, offset=offset)
    results = []
    for r in reviews:
        results.append(
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
                findings_count=len(r.findings),
                created_at=r.created_at
            )
        )
    return results


@router.get("/stats/dashboard", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ReviewService(db)
    return service.get_dashboard_stats(current_user.id)


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review_detail(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ReviewService(db)
    review = service.get_review_by_id(review_id, current_user.id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ReviewService(db)
    deleted = service.delete_review(review_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found.")
    return None
