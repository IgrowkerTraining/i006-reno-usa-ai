from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from app.db.models.prompt_template import PromptTemplateDB
from app.models.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse,
    PromptTemplateListItem,
    ActivePromptResponse
)

class PromptTemplateService:
    """Service para operaciones CRUD de Prompt Templates"""
    
    @staticmethod
    def get_active_prompt(db: Session) -> Optional[ActivePromptResponse]:
        """Obtiene el prompt activo en el sistema."""
        active_prompt = db.query(PromptTemplateDB).filter(
            PromptTemplateDB.activo == True
        ).order_by(
            desc(PromptTemplateDB.version),
            desc(PromptTemplateDB.fecha_creacion)
        ).first()
        
        if not active_prompt:
            return None
            
        return ActivePromptResponse.model_validate(active_prompt)

    @staticmethod
    def create_prompt_template(db: Session, prompt_data: PromptTemplateCreate) -> PromptTemplateResponse:
        """Crea un nuevo prompt template."""
        existing = db.query(PromptTemplateDB).filter(
            PromptTemplateDB.nombre_codigo == prompt_data.nombre_codigo
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un prompt template con el código '{prompt_data.nombre_codigo}'"
            )
            
        new_prompt = PromptTemplateDB(**prompt_data.model_dump())
        db.add(new_prompt)
        db.commit()
        db.refresh(new_prompt)
        return PromptTemplateResponse.model_validate(new_prompt)

    @staticmethod
    def get_prompt_template_by_id(db: Session, prompt_id: int) -> PromptTemplateResponse:
        """Obtiene un prompt template por su ID."""
        prompt = db.query(PromptTemplateDB).filter(PromptTemplateDB.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Prompt {prompt_id} no encontrado")
        return PromptTemplateResponse.model_validate(prompt)
    
    @staticmethod
    def get_all_prompt_templates(db: Session, skip: int = 0, limit: int = 100, activo_only: bool = False) -> List[PromptTemplateListItem]:
        """Obtiene todos los prompt templates."""
        query = db.query(PromptTemplateDB)
        if activo_only:
            query = query.filter(PromptTemplateDB.activo == True)
            
        prompts = query.order_by(desc(PromptTemplateDB.fecha_creacion)).offset(skip).limit(limit).all()
        return [PromptTemplateListItem.model_validate(p) for p in prompts]
    
    @staticmethod
    def update_prompt_template(db: Session, prompt_id: int, prompt_update: PromptTemplateUpdate) -> PromptTemplateResponse:
        """Actualiza un prompt template existente."""
        prompt = db.query(PromptTemplateDB).filter(PromptTemplateDB.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Prompt {prompt_id} no encontrado")
        
        update_data = prompt_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prompt, field, value)
            
        db.commit()
        db.refresh(prompt)
        return PromptTemplateResponse.model_validate(prompt)
    
    @staticmethod
    def deactivate_prompt_template(db: Session, prompt_id: int) -> PromptTemplateResponse:
        """Desactiva un prompt template."""
        prompt = db.query(PromptTemplateDB).filter(PromptTemplateDB.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Prompt {prompt_id} no encontrado")
            
        prompt.activo = False
        db.commit()
        db.refresh(prompt)
        return PromptTemplateResponse.model_validate(prompt)
    
    @staticmethod
    def activate_prompt_template(db: Session, prompt_id: int) -> PromptTemplateResponse:
        """Activa un prompt template y desactiva todos los demás."""
        prompt = db.query(PromptTemplateDB).filter(PromptTemplateDB.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Prompt {prompt_id} no encontrado")
            
        # Desactivar todos los prompts
        db.query(PromptTemplateDB).update({"activo": False})
        
        # Activar el seleccionado
        prompt.activo = True
        db.commit()
        db.refresh(prompt)
        return PromptTemplateResponse.model_validate(prompt)
    
    @staticmethod
    def delete_prompt_template(db: Session, prompt_id: int) -> dict:
        """Elimina un prompt template (hard delete)."""
        prompt = db.query(PromptTemplateDB).filter(PromptTemplateDB.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Prompt {prompt_id} no encontrado")
            
        if prompt.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No se puede eliminar un prompt activo. Desactívalo primero."
            )
            
        db.delete(prompt)
        db.commit()
        return {"message": f"Prompt template {prompt_id} eliminado exitosamente"}