from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.api.auth import get_current_user
from app.schemas.github import GitHubAnalyzeRequest, GitHubAnalysisResponse
from app.services.github_service import GitHubService

router = APIRouter(prefix="/github", tags=["GitHub"])


@router.post("/analyze", response_model=GitHubAnalysisResponse)
async def analyze_github_repo(
    request: GitHubAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = GitHubService(db)
    try:
        response = await service.analyze_repository(current_user.id, request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GitHub repository analysis failed: {str(e)}"
        )
