from fastapi import APIRouter
from app.ai.ollama_provider import OllamaProvider
from app.ai.mock_provider import MockAIProvider
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
async def get_health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER
    }


@router.get("/ollama")
async def get_ollama_health():
    if settings.AI_PROVIDER == "mock":
        provider = MockAIProvider()
        return await provider.check_health()
    provider = OllamaProvider()
    return await provider.check_health()
