from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse,
    PromptTemplateListItem,
    ActivePromptResponse
)
from app.services.prompt_template_service import PromptTemplateService


# Router para prompts
router = APIRouter(
    prefix="/api/v1/prompts",
    tags=["Prompt Templates"]
)


@router.post(
    "/",
    response_model=PromptTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo prompt template",
    description="Crea un nuevo prompt template en el sistema"
)
def create_prompt_template(
    prompt_data: PromptTemplateCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo prompt template.
    
    - **nombre_codigo**: Código único del prompt
    - **version**: Número de versión
    - **template_text**: Texto completo del prompt
    - **activo**: Si está activo o no (default: true)
    """
    return PromptTemplateService.create_prompt_template(db, prompt_data)


@router.get(
    "/",
    response_model=List[PromptTemplateListItem],
    summary="Listar todos los prompts",
    description="Obtiene una lista de todos los prompt templates"
)
def get_all_prompts(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Cantidad máxima de registros"),
    activo_only: bool = Query(False, description="Solo prompts activos"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los prompt templates con paginación.
    
    - **skip**: Cantidad de registros a saltar (para paginación)
    - **limit**: Cantidad máxima de registros a devolver
    - **activo_only**: Si es true, solo devuelve prompts activos
    """
    return PromptTemplateService.get_all_prompt_templates(db, skip, limit, activo_only)


@router.get(
    "/active",
    response_model=ActivePromptResponse,
    summary="Obtener el prompt activo",
    description="Obtiene el prompt template activo más reciente"
)
def get_active_prompt(db: Session = Depends(get_db)):
    """
    Obtiene el prompt template que está actualmente activo.
    
    Este es el prompt que se usará por defecto para generar análisis.
    """
    active = PromptTemplateService.get_active_prompt(db)
    
    if not active:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay ningún prompt activo en el sistema"
        )
    
    return active


@router.get(
    "/{prompt_id}",
    response_model=PromptTemplateResponse,
    summary="Obtener un prompt por ID",
    description="Obtiene los detalles completos de un prompt template específico"
)
def get_prompt_by_id(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un prompt template por su ID.
    
    - **prompt_id**: ID del prompt template
    """
    return PromptTemplateService.get_prompt_template_by_id(db, prompt_id)


@router.put(
    "/{prompt_id}",
    response_model=PromptTemplateResponse,
    summary="Actualizar un prompt",
    description="Actualiza los datos de un prompt template existente"
)
def update_prompt(
    prompt_id: int,
    prompt_update: PromptTemplateUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un prompt template.
    
    - **prompt_id**: ID del prompt a actualizar
    - **template_text**: Nuevo texto del template (opcional)
    - **activo**: Nuevo estado activo/inactivo (opcional)
    """
    return PromptTemplateService.update_prompt_template(db, prompt_id, prompt_update)


@router.patch(
    "/{prompt_id}/activate",
    response_model=PromptTemplateResponse,
    summary="Activar un prompt",
    description="Activa un prompt y desactiva todos los demas"
)
def activate_prompt(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    """
    Activa un prompt template especifico y desactiva todos los demas.
    
    Solo puede haber un prompt activo a la vez.
    
    - **prompt_id**: ID del prompt a activar
    """
    return PromptTemplateService.activate_prompt_template(db, prompt_id)


@router.patch(
    "/{prompt_id}/deactivate",
    response_model=PromptTemplateResponse,
    summary="Desactivar un prompt",
    description="Desactiva un prompt template"
)
def deactivate_prompt(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    """
    Desactiva un prompt template.
    
    - **prompt_id**: ID del prompt a desactivar
    """
    return PromptTemplateService.deactivate_prompt_template(db, prompt_id)


@router.delete(
    "/{prompt_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar un prompt",
    description="Elimina permanentemente un prompt template"
)
def delete_prompt(
    prompt_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un prompt template de forma permanente.
    
    **IMPORTANTE**: No se puede eliminar un prompt que este activo.
    Desactivalo primero.
    
    - **prompt_id**: ID del prompt a eliminar
    """
    return PromptTemplateService.delete_prompt_template(db, prompt_id)
