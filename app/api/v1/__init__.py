"""API v1 endpoints."""

from fastapi import APIRouter
from app.api.v1 import chat, health
from app.api.v1.prompt_template_route import router as prompt_router

api_router = APIRouter(prefix="/api/v1")

# Include all v1 routers
api_router.include_router(chat.router)
api_router.include_router(health.router)
api_router.include_router(prompt_router)