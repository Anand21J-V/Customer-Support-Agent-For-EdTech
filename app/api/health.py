"""Health check endpoint."""

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return service health status."""
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
    }
