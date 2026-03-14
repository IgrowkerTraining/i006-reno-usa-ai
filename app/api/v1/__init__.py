"""API v1 endpoints."""

from fastapi import APIRouter
from . import chat, health, reportes, logs, prompts

api_router = APIRouter(prefix="/api/v1") 

# Enchufamos todo
api_router.include_router(chat.router)
api_router.include_router(health.router)
api_router.include_router(reportes.router)
api_router.include_router(logs.router)
api_router.include_router(prompts.router)