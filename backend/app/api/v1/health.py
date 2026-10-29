from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.redis_client import is_available as redis_available

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "sentinel-ai-backend",
        "environment": settings.environment,
        "simulation_mode": settings.simulation_mode,
    }


@router.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict:
    """Readiness probe: verifies database and Redis connectivity.

    Never raises — a dependency being down is reported in the payload so
    the app stays up and callers can degrade gracefully (PRD section 52).
    """
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except SQLAlchemyError:
        db_ok = False

    redis_ok = redis_available()

    return {
        "status": "ready" if (db_ok and redis_ok) else "degraded",
        "database": "up" if db_ok else "down",
        "redis": "up" if redis_ok else "down",
    }
