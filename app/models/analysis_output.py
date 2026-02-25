"""
Schemas para Analysis Output
Estructura del análisis generado por la IA
"""

from typing import List
from pydantic import BaseModel, Field

from .enums import RiskLevel


class AnalysisOutput(BaseModel):
    """
    Resultado del análisis generado por la IA.
    Este es el output estructurado que devuelve OpenRouter después de procesar.
    """
    
    general_project_status: str = Field(
        ..., 
        min_length=50,
        description="Resumen general del estado del proyecto en el período analizado"
    )
    
    execution_schedule_analysis: str = Field(
        ...,
        min_length=50,
        description="Análisis detallado de la ejecución y el cumplimiento del cronograma"
    )
    
    safety_compliance_analysis: str = Field(
        ...,
        min_length=50,
        description="Análisis del cumplimiento de medidas de seguridad y normativas"
    )
    
    technical_approvals_analysis: str = Field(
        ...,
        min_length=30,
        description="Análisis de las aprobaciones técnicas y validaciones profesionales"
    )
    
    overall_observation: str = Field(
        ...,
        min_length=50,
        description="Observación general consolidada del proyecto"
    )
    
    risk_level: RiskLevel = Field(
        ...,
        description="Nivel de riesgo operativo y de cumplimiento identificado"
    )
    
    detected_inconsistencies: List[str] = Field(
        default_factory=list,
        description="Lista de inconsistencias o alertas detectadas en el análisis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "general_project_status": "During the analyzed period, the project shows progress consistent with the planned phase of interior framing. The registered tasks align with the expected activities for the current phase, and no critical inconsistencies are identified between active trades and executed work.",
                "execution_schedule_analysis": "The declared phase completion of 60% reflects a minor deviation from the original schedule, with a reported delay of one day due to material delivery. Historical patterns indicate that delays of this type and duration are common in similar project phases and do not represent a critical risk at this stage.",
                "safety_compliance_analysis": "The safety measures declared for the period are consistent with the type of work performed and the trades present on site. Required personal protective equipment and fall protection measures are reported as implemented. Worker coverage is declared as active under a Workers' Compensation policy. No safety-related incidents are reported for the analyzed period.",
                "technical_approvals_analysis": "The current project phase is marked as approved by the assigned licensed professional. No discrepancies are detected between the recorded execution data and the technical approval status.",
                "overall_observation": "Based on the information recorded, the project presents a stable operational state for the analyzed period. The combination of minor schedule deviation, consistent safety reporting and valid technical approval indicates low operational and compliance risk at this time.",
                "risk_level": "low",
                "detected_inconsistencies": []
            }
        }
