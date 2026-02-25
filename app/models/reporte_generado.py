"""
Schemas para Reportes Generados
Gestión de los análisis generados por la IA + Schemas de API
"""

from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from .project_snapshot import ProjectSnapshot
from .analysis_output import AnalysisOutput
from .enums import RiskLevel


# ============================================================================
# DATABASE SCHEMAS (para la tabla reportes_generados)
# ============================================================================

class ReporteGeneradoCreate(BaseModel):
    """Schema para crear un nuevo reporte de análisis"""
    project_id: str = Field(
        ..., 
        description="Código del proyecto en el backend (ej: RENO-US-2026-009)"
    )
    fase_analizada: str = Field(
        ..., 
        description="Nombre de la fase analizada (ej: 'Interior framing')"
    )
    input_snapshot: ProjectSnapshot = Field(
        ..., 
        description="Snapshot completo recibido del backend"
    )
    prompt_version_id: int = Field(
        ..., 
        description="ID de la versión del prompt template utilizada"
    )


class ReporteGeneradoResponse(BaseModel):
    """Schema de respuesta con el reporte completo desde la DB"""
    id: UUID
    project_id: str
    fase_analizada: str
    fecha_generacion: datetime
    input_snapshot: Dict[str, Any]
    output_analisis: AnalysisOutput
    modelo_utilizado: str
    prompt_version_id: int

    model_config = ConfigDict(from_attributes=True)


class ReporteGeneradoListItem(BaseModel):
    """Schema resumido para listado de reportes"""
    id: UUID
    project_id: str
    fase_analizada: str
    fecha_generacion: datetime
    risk_level: RiskLevel
    modelo_utilizado: str

    model_config = ConfigDict(from_attributes=True)


class ReporteGeneradoDetailResponse(BaseModel):
    """Schema detallado para consulta individual de reporte"""
    id: UUID
    project_id: str
    fase_analizada: str
    fecha_generacion: datetime
    analysis: AnalysisOutput
    modelo_utilizado: str
    prompt_version_id: int
    
    # Metadata adicional
    tokens_used: int
    execution_time_ms: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# API REQUEST/RESPONSE SCHEMAS (para los endpoints)
# ============================================================================

class GenerateAnalysisRequest(BaseModel):
    """
    Request para generar un nuevo análisis.
    Este es el endpoint principal que llama el backend.
    """
    snapshot: ProjectSnapshot = Field(
        ..., 
        description="Snapshot del proyecto a analizar"
    )
    prompt_template_name: str | None = Field(
        None,
        description="Nombre del prompt template a usar (usa el activo por defecto si no se especifica)"
    )


class GenerateAnalysisResponse(BaseModel):
    """
    Response después de generar un análisis exitosamente.
    """
    report_id: UUID
    project_id: str
    analysis: AnalysisOutput
    generated_at: datetime
    tokens_used: int
    execution_time_ms: int
    model_used: str
