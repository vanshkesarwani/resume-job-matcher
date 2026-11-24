from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("", summary="Service Health Check")
def check_health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }

