"""
Schemas para Project Snapshot
Estructura de datos que recibe el servicio desde el backend
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ProjectSnapshot(BaseModel):
    """
    Snapshot completo del proyecto enviado desde el backend.
    Contiene toda la información de un período específico para análisis.
    """
    
    # Identificación del proyecto
    project_code: str = Field(
        ..., 
        description="Código único del proyecto (ej: RENO-US-2026-009)",
        pattern=r"^RENO-US-\d{4}-\d{3}$"
    )
    project_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre descriptivo del proyecto"
    )
    location: str = Field(
        ...,
        description="Ubicación del proyecto"
    )
    
    # Período analizado
    period_start: datetime = Field(
        ..., 
        description="Fecha de inicio del período analizado"
    )
    period_end: datetime = Field(
        ..., 
        description="Fecha de fin del período analizado"
    )
    
    # Estado de la fase actual
    current_phase: str = Field(
        ...,
        description="Nombre de la fase actual del proyecto (ej: 'Interior framing')"
    )
    phase_completion_percentage: float = Field(
        ..., 
        ge=0, 
        le=100,
        description="Porcentaje de completitud de la fase actual"
    )
    schedule_deviation_days: int = Field(
        ..., 
        description="Desvío del cronograma en días (+ adelantado, - atrasado)"
    )
    
    # Ejecución
    tasks_performed: List[str] = Field(
        default_factory=list,
        description="Lista de tareas ejecutadas en el período"
    )
    
    # Trades (oficios)
    trades_on_site: List[str] = Field(
        default_factory=list,
        description="Lista de trades presentes en obra durante el período"
    )
    
    # Seguridad
    safety_measures: List[str] = Field(
        default_factory=list,
        description="Medidas de seguridad implementadas"
    )
    
    # Cobertura de trabajadores
    worker_coverage: Dict[str, Any] = Field(
        default_factory=dict,
        description="Información de aseguramiento de trabajadores"
    )
    
    # Aprobaciones técnicas
    technical_approval: Dict[str, Any] = Field(
        default_factory=dict,
        description="Información de aprobación técnica del licensed professional"
    )
    
    # Incidentes
    incidents_reported: int = Field(
        default=0, 
        ge=0,
        description="Número de incidentes reportados en el período"
    )
    
    # Notas adicionales
    supervisor_notes: Optional[str] = Field(
        None,
        description="Notas adicionales del supervisor"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "project_code": "RENO-US-2026-009",
                "project_name": "Residential Remodeling – Montecito",
                "location": "Montecito, California",
                "period_start": "2026-04-01T00:00:00Z",
                "period_end": "2026-04-22T23:59:59Z",
                "current_phase": "Interior framing",
                "phase_completion_percentage": 60.0,
                "schedule_deviation_days": 1,
                "tasks_performed": [
                    "Drywall installation",
                    "Electrical rough-in",
                    "HVAC duct placement"
                ],
                "trades_on_site": [
                    "Framing crew",
                    "Electrical contractor",
                    "HVAC contractor"
                ],
                "safety_measures": [
                    "Hard hats and PPE enforced",
                    "Fall protection installed",
                    "Electrical lockout/tagout applied"
                ],
                "worker_coverage": {
                    "coverage_type": "Workers' Compensation",
                    "policy_reference": "WC-CA-882134",
                    "status": "Active"
                },
                "technical_approval": {
                    "licensed_professional": "Michael Anderson, Architect",
                    "approval_status": "Approved",
                    "approval_date": "2026-04-22"
                },
                "incidents_reported": 0,
                "supervisor_notes": "Minor delay due to material delivery"
            }
        }
