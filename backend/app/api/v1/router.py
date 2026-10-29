from fastapi import APIRouter

from app.api.v1 import agents, approvals, auth, events, health, incidents, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/api/v1")
api_router.include_router(users.router, prefix="/api/v1")
api_router.include_router(events.router, prefix="/api/v1")
api_router.include_router(incidents.router, prefix="/api/v1")
api_router.include_router(agents.router, prefix="/api/v1")
api_router.include_router(approvals.router, prefix="/api/v1")
