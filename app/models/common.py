"""
Schemas comunes utilizados en múltiples partes del sistema
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Schema estándar de respuesta de error"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    """Response del health check del servicio"""
    status: str
    timestamp: datetime
    database_connected: bool
    openrouter_configured: bool


class PaginationParams(BaseModel):
    """Parámetros de paginación estándar"""
    page: int = Field(default=1, ge=1, description="Número de página")
    page_size: int = Field(default=20, ge=1, le=100, description="Elementos por página")


class PaginatedResponse(BaseModel):
    """Response paginado genérico"""
    total: int
    page: int
    page_size: int
    total_pages: int
