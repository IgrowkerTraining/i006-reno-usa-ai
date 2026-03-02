from typing import List
from fastapi import APIRouter, Depends, status, Query, HTTPException
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

router = APIRouter(prefix="/prompts", tags=["Prompt Templates"])

@router.post("/", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo prompt")
def create_prompt_template(prompt_data: PromptTemplateCreate, db: Session = Depends(get_db)):
    """Crea un nuevo prompt template en el sistema."""
    return PromptTemplateService.create_prompt_template(db, prompt_data)

@router.get("/", response_model=List[PromptTemplateListItem], summary="Listar todos los prompts")
def get_all_prompts(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Cantidad máxima de registros"),
    activo_only: bool = Query(False, description="Solo prompts activos"),
    db: Session = Depends(get_db)
):
    """Obtiene todos los prompt templates con paginación."""
    return PromptTemplateService.get_all_prompt_templates(db, skip, limit, activo_only)

@router.get("/active", response_model=ActivePromptResponse, summary="Obtener el prompt activo")
def get_active_prompt(db: Session = Depends(get_db)):
    """Obtiene el prompt template que está actualmente activo."""
    active = PromptTemplateService.get_active_prompt(db)
    if not active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay ningún prompt activo en el sistema")
    return active

@router.get("/{prompt_id}", response_model=PromptTemplateResponse, summary="Obtener un prompt por ID")
def get_prompt_by_id(prompt_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles completos de un prompt template específico."""
    return PromptTemplateService.get_prompt_template_by_id(db, prompt_id)

@router.put("/{prompt_id}", response_model=PromptTemplateResponse, summary="Actualizar un prompt")
def update_prompt(prompt_id: int, prompt_update: PromptTemplateUpdate, db: Session = Depends(get_db)):
    """Actualiza los datos de un prompt template existente."""
    return PromptTemplateService.update_prompt_template(db, prompt_id, prompt_update)

@router.patch("/{prompt_id}/activate", response_model=PromptTemplateResponse, summary="Activar un prompt")
def activate_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Activa un prompt template especifico y desactiva todos los demas."""
    return PromptTemplateService.activate_prompt_template(db, prompt_id)

@router.patch("/{prompt_id}/deactivate", response_model=PromptTemplateResponse, summary="Desactivar un prompt")
def deactivate_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Desactiva un prompt template."""
    return PromptTemplateService.deactivate_prompt_template(db, prompt_id)

@router.delete("/{prompt_id}", status_code=status.HTTP_200_OK, summary="Eliminar un prompt")
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """Elimina un prompt template de forma permanente. (Debe estar inactivo)."""
    return PromptTemplateService.delete_prompt_template(db, prompt_id)