"""Health check API routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.models.appointment import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns service health status, version, and current timestamp.",
)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Verify the API is running and responsive."""
    return HealthResponse(
        service=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
