"""
Schemas para Prompt Templates
Gestión de plantillas de prompts versionadas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class PromptTemplateBase(BaseModel):
    nombre_codigo: str = Field(..., min_length=1, max_length=100)
    version: int = Field(..., ge=1)
    template_text: str = Field(..., min_length=10)
    activo: bool = Field(default=True)

class PromptTemplateCreate(PromptTemplateBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre_codigo": "auditor_base",
                "version": 1,
                "template_text": "You are an expert construction project auditor for Reno USA. Analyze the following project data snapshot and return ONLY a valid JSON object. ALL text responses MUST be written in English. The JSON must STRICTLY comply with this structure (no extra text, no greetings, no markdown blocks): {\"general_project_status\": \"descriptive text in English\", \"execution_schedule_analysis\": \"descriptive text in English\", \"safety_compliance_analysis\": \"descriptive text in English\", \"technical_approvals_analysis\": \"descriptive text in English\", \"overall_observation\": \"detailed general observation in English, MUST BE LONGER THAN 50 CHARACTERS.\", \"risk_level\": \"low\", \"medium\", or \"high\", \"detected_inconsistencies\": [\"inconsistency 1\"] or [] if none}",
                "activo": True
            }
        }
    )

class PromptTemplateUpdate(BaseModel):
    template_text: Optional[str] = Field(None, min_length=10)
    activo: Optional[bool] = Field(None)

class PromptTemplateResponse(PromptTemplateBase):
    id: int
    fecha_creacion: datetime
    model_config = ConfigDict(from_attributes=True)

class PromptTemplateListItem(BaseModel):
    id: int
    nombre_codigo: str
    version: int
    activo: bool
    fecha_creacion: datetime
    model_config = ConfigDict(from_attributes=True)

class ActivePromptResponse(BaseModel):
    id: int
    nombre_codigo: str
    version: int
    template_text: str
    fecha_creacion: datetime
    model_config = ConfigDict(from_attributes=True)