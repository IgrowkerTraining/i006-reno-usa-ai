from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from .project_snapshot import ProjectSnapshot
from .analysis_output import AnalysisOutput

# ============================================================================
# DATABASE SCHEMAS (para la tabla reportes_generados)
# ============================================================================

class ReporteGeneradoCreate(BaseModel):
    project_id: str = Field(..., description="Nombre del proyecto")
    fase_analizada: str = Field(..., description="Nombre de la fase analizada")
    input_snapshot: ProjectSnapshot = Field(..., description="Snapshot completo recibido del backend")
    prompt_version_id: int = Field(..., description="ID de la versión del prompt template utilizada")

class ReporteGeneradoResponse(BaseModel):
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
    id: UUID
    project_id: str
    fase_analizada: str
    fecha_generacion: datetime
    modelo_utilizado: str

    model_config = ConfigDict(from_attributes=True)

class ReporteGeneradoDetailResponse(BaseModel):
    id: UUID
    project_id: str
    fase_analizada: str
    fecha_generacion: datetime
    analysis: AnalysisOutput
    modelo_utilizado: str
    prompt_version_id: int
    tokens_used: int
    execution_time_ms: int

    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# API REQUEST/RESPONSE SCHEMAS (para los endpoints)
# ============================================================================

class GenerateAnalysisRequest(BaseModel):
    snapshot: ProjectSnapshot = Field(..., description="Snapshot del proyecto a analizar")

class GenerateAnalysisResponse(BaseModel):
    report_id: UUID
    project_id: str
    analysis: AnalysisOutput
    generated_at: datetime
    tokens_used: int
    execution_time_ms: int
    model_used: str
