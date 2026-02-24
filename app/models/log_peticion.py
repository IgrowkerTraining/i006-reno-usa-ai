"""
Schemas para Log de Peticiones
Trazabilidad de las llamadas al servicio de LLM
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# DATABASE SCHEMAS (para la tabla log_peticiones)
# ============================================================================

class LogPeticionCreate(BaseModel):
    """Schema para crear un log de petición al LLM"""
    reporte_id: UUID = Field(
        ..., 
        description="UUID del reporte asociado"
    )
    tokens_entrada: int = Field(
        ..., 
        ge=0,
        description="Cantidad de tokens de entrada (prompt)"
    )
    tokens_salida: int = Field(
        ..., 
        ge=0,
        description="Cantidad de tokens de salida (respuesta)"
    )
    costo_estimado: float = Field(
        ..., 
        ge=0,
        description="Costo estimado de la petición en USD"
    )
    tiempo_ejecucion_ms: int = Field(
        ..., 
        ge=0,
        description="Tiempo de ejecución en milisegundos"
    )
    status_code: int = Field(
        ...,
        description="Código de estado HTTP de la respuesta"
    )


# ============================================================================
# RESPONSE SCHEMAS (para consultas desde la DB)
# ============================================================================

class LogPeticionResponse(BaseModel):
    """Schema de respuesta para logs de peticiones"""
    id: int
    reporte_id: UUID
    tokens_entrada: int
    tokens_salida: int
    costo_estimado: float
    tiempo_ejecucion_ms: int
    status_code: int
    fecha_evento: datetime

    model_config = ConfigDict(from_attributes=True)


class LogPeticionSummary(BaseModel):
    """Schema resumido para estadísticas de logs"""
    total_peticiones: int
    total_tokens_entrada: int
    total_tokens_salida: int
    costo_total: float
    tiempo_promedio_ms: float
    tasa_exito: float  # Porcentaje de peticiones exitosas


class LogPeticionDetailResponse(BaseModel):
    """Schema detallado para consulta individual de log"""
    id: int
    reporte_id: UUID
    tokens_entrada: int
    tokens_salida: int
    tokens_totales: int
    costo_estimado: float
    tiempo_ejecucion_ms: int
    status_code: int
    fecha_evento: datetime
    
    # Metadata calculada
    exitoso: bool
    costo_por_token: float

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# QUERY SCHEMAS (para filtrar logs)
# ============================================================================

class LogPeticionFilters(BaseModel):
    """Filtros para consultar logs"""
    reporte_id: UUID | None = None
    fecha_desde: datetime | None = None
    fecha_hasta: datetime | None = None
    status_code: int | None = None
    min_tokens: int | None = Field(None, ge=0)
    max_tokens: int | None = Field(None, ge=0)
