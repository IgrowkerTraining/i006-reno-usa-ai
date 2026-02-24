"""
Schemas para Prompt Templates
Gestión de plantillas de prompts versionadas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class PromptTemplateBase(BaseModel):
    """Schema base para prompt templates"""
    nombre_codigo: str = Field(
        ..., 
        min_length=1,
        max_length=100,
        description="Código único identificador del prompt"
    )
    version: int = Field(
        ..., 
        ge=1,
        description="Número de versión del prompt"
    )
    template_text: str = Field(
        ..., 
        min_length=10,
        description="Texto completo del template del prompt"
    )
    activo: bool = Field(
        default=True, 
        description="Indica si esta versión está activa"
    )


# ============================================================================
# CREATE/UPDATE SCHEMAS
# ============================================================================

class PromptTemplateCreate(PromptTemplateBase):
    """Schema para crear un nuevo prompt template"""
    pass


class PromptTemplateUpdate(BaseModel):
    """Schema para actualizar un prompt template existente"""
    template_text: Optional[str] = Field(
        None,
        min_length=10,
        description="Nuevo texto del template"
    )
    activo: Optional[bool] = Field(
        None,
        description="Cambiar estado activo/inactivo"
    )


# ============================================================================
# RESPONSE SCHEMAS (para consultas desde la DB)
# ============================================================================

class PromptTemplateResponse(PromptTemplateBase):
    """Schema de respuesta con datos completos del prompt template"""
    id: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptTemplateListItem(BaseModel):
    """Schema resumido para listado de prompts"""
    id: int
    nombre_codigo: str
    version: int
    activo: bool
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)


class ActivePromptResponse(BaseModel):
    """Schema para obtener el prompt activo actual"""
    id: int
    nombre_codigo: str
    version: int
    template_text: str
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)
