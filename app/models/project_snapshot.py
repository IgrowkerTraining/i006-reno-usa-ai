"""
Schemas para Project Snapshot
Estructura de datos que recibe el servicio desde el backend
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class TaskSnapshotItem(BaseModel):
    """
    Representa una tarea individual plana dentro del snapshot del proyecto.
    """
    name: str
    phase: str
    status: str
    is_incidence: bool
    category: Optional[str] = None

class ProjectSnapshot(BaseModel):
    """
    Snapshot completo del proyecto enviado desde el backend Node.js.
    """
    
    # --- Nuevos campos obligatorios para el Dashboard de IA ---
    project_id: str = Field(
        ..., 
        description="ID único del proyecto (ej: el CUID de la base de datos de Node)"
    )
    project_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre descriptivo del proyecto"
    )
    active_phase: str = Field(
        ...,
        description="Nombre de la fase actual del proyecto (donde hay tareas en curso)"
    )
    tasks_snapshot: List[TaskSnapshotItem] = Field(
        ...,
        description="Lista plana de todas las tareas del proyecto, sus estados y categorías"
    )

    # --- Campos Legacy / Opcionales ---
    # Los dejamos como opcionales para no romper compatibilidad con llamadas viejas
    project_code: Optional[str] = Field(None, description="Código único del proyecto")
    current_phase: Optional[str] = Field(None, description="Legacy: Nombre de la fase actual")
    phase_progress_percentage: Optional[float] = Field(None, description="Legacy: Porcentaje pre-calculado")
    total_tasks_count: Optional[int] = Field(None, description="Legacy: Cantidad de tareas")
    in_process_tasks: Optional[List[str]] = Field(default_factory=list)
    tasks_sequence: Optional[List[Any]] = Field(default_factory=list)
    
    location: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    schedule_deviation_days: Optional[int] = 0
    tasks_performed: Optional[List[str]] = Field(default_factory=list)
    trades_on_site: Optional[List[str]] = Field(default_factory=list)
    safety_measures: Optional[List[str]] = Field(default_factory=list)
    worker_coverage: Optional[Dict[str, Any]] = Field(default_factory=dict)
    technical_approval: Optional[Dict[str, Any]] = Field(default_factory=dict)
    incidents_reported: Optional[int] = 0
    supervisor_notes: Optional[str] = None
    # ----------------------------------

    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "Project Gamma",
                "active_phase": "Installations",
                "tasks_snapshot": [
                    {
                        "name": "Fire Safety",
                        "phase": "Installations",
                        "status": "completed",
                        "is_incidence": False,
                        "category": None
                    },
                    {
                        "name": "Electrical Connection Analysis",
                        "phase": "Installations",
                        "status": "pending",
                        "is_incidence": True,
                        "category": "ELECTRICAL"
                    }
                ]
            }
        }