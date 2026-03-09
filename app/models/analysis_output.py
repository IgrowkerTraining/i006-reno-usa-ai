"""
Schemas para Analysis Output
Estructura matemática del análisis generado por la IA para el Dashboard
"""

from typing import List
from pydantic import BaseModel, Field

class AnalysisOutput(BaseModel):
    """
    Resultado del análisis generado por la IA.
    Este es el output estructurado matemático que devuelve el modelo para armar la UI.
    """
    
    # --- Progress Metrics ---
    advancePercentage: int = Field(
        ..., 
        description="Integer percentage of overall progress (completed tasks / total tasks) * 100. Returns 0 if there are no tasks."
    )
    completedTasksCount: int = Field(
        ..., 
        description="Total absolute count of completed tasks in the project."
    )
    uncompletedTasksCount: int = Field(
        ..., 
        description="Total absolute count of uncompleted tasks (pending or in_progress) in the project."
    )
    
    # --- Active Phase details ---
    inProcessTasks: List[str] = Field(
        default_factory=list, 
        description="List of names of the tasks that are 'pending' or 'in_progress' specifically in the currently active phase."
    )
    
    # --- Incidence Metrics (Percentages and absolute counts) ---
    safetyPercent: int = Field(
        ..., 
        description="Integer percentage of SAFETY incidences over the total number of tasks."
    )
    safetyCount: int = Field(
        ..., 
        description="Total absolute count of active SAFETY incidences."
    )
    
    electricalPercent: int = Field(
        ..., 
        description="Integer percentage of ELECTRICAL incidences over the total number of tasks."
    )
    electricalCount: int = Field(
        ..., 
        description="Total absolute count of active ELECTRICAL incidences."
    )
    
    correctionPercent: int = Field(
        ..., 
        description="Integer percentage of CORRECTION incidences over the total number of tasks."
    )
    correctionCount: int = Field(
        ..., 
        description="Total absolute count of active CORRECTION incidences."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "advancePercentage": 65,
                "completedTasksCount": 65,
                "uncompletedTasksCount": 35,
                "inProcessTasks": [
                    "Project Planning", 
                    "Electrical Installation", 
                    "Fire extinguisher service",
                    "Plumber registration"
                ],
                "safetyPercent": 3,
                "safetyCount": 2,
                "electricalPercent": 3,
                "electricalCount": 2,
                "correctionPercent": 3,
                "correctionCount": 2
            }
        }
