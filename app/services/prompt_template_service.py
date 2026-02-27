from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from app.db.prompt_template_models import PromptTemplateModel
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
    def create_prompt_template(
        db: Session, 
        prompt_data: PromptTemplateCreate
    ) -> PromptTemplateResponse:
        """
        Crea un nuevo prompt template.
        
        Args:
            db: Sesión de base de datos
            prompt_data: Datos del prompt a crear
            
        Returns:
            PromptTemplateResponse con el prompt creado
            
        Raises:
            HTTPException 400: Si ya existe un prompt con ese código
        """
        # Verificar si ya existe un prompt con ese nombre_codigo
        existing = db.query(PromptTemplateModel).filter(
            PromptTemplateModel.nombre_codigo == prompt_data.nombre_codigo
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un prompt template con el código '{prompt_data.nombre_codigo}'"
            )
        
        # Crear el nuevo prompt
        new_prompt = PromptTemplateModel(
            nombre_codigo=prompt_data.nombre_codigo,
            version=prompt_data.version,
            template_text=prompt_data.template_text,
            activo=prompt_data.activo
        )
        
        db.add(new_prompt)
        db.commit()
        db.refresh(new_prompt)
        
        return PromptTemplateResponse.model_validate(new_prompt)
    
    @staticmethod
    def get_prompt_template_by_id(
        db: Session, 
        prompt_id: int
    ) -> PromptTemplateResponse:
        """
        Obtiene un prompt template por su ID.
        
        Args:
            db: Sesión de base de datos
            prompt_id: ID del prompt template
            
        Returns:
            PromptTemplateResponse con los datos del prompt
            
        Raises:
            HTTPException 404: Si no se encuentra el prompt
        """
        prompt = db.query(PromptTemplateModel).filter(
            PromptTemplateModel.id == prompt_id
        ).first()
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt template con ID {prompt_id} no encontrado"
            )
        
        return PromptTemplateResponse.model_validate(prompt)
    
    @staticmethod
    def get_all_prompt_templates(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        activo_only: bool = False
    ) -> List[PromptTemplateListItem]:
        """
        Obtiene todos los prompt templates.
        
        Args:
            db: Sesión de base de datos
            skip: Cantidad de registros a saltar (paginación)
            limit: Cantidad máxima de registros a devolver
            activo_only: Si es True, solo devuelve prompts activos
            
        Returns:
            Lista de PromptTemplateListItem
        """
        query = db.query(PromptTemplateModel)
        
        if activo_only:
            query = query.filter(PromptTemplateModel.activo == True)
        
        prompts = query.order_by(
            desc(PromptTemplateModel.fecha_creacion)
        ).offset(skip).limit(limit).all()
        
        return [PromptTemplateListItem.model_validate(p) for p in prompts]
    
    @staticmethod
    def get_active_prompt(db: Session) -> Optional[ActivePromptResponse]:
        """
        Obtiene el prompt template activo más reciente.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            ActivePromptResponse con el prompt activo o None si no hay ninguno
        """
        active_prompt = db.query(PromptTemplateModel).filter(
            PromptTemplateModel.activo == True
        ).order_by(
            desc(PromptTemplateModel.version),
            desc(PromptTemplateModel.fecha_creacion)
        ).first()
        
        if not active_prompt:
            return None
        
        return ActivePromptResponse.model_validate(active_prompt)
    
    @staticmethod
    def update_prompt_template(
        db: Session,
        prompt_id: int,
        prompt_update: PromptTemplateUpdate
    ) -> PromptTemplateResponse:
        """
        Actualiza un prompt template existente.
        
        Args:
            db: Sesión de base de datos
            prompt_id: ID del prompt a actualizar
            prompt_update: Datos a actualizar
            
        Returns:
            PromptTemplateResponse con el prompt actualizado
            
        Raises:
            HTTPException 404: Si no se encuentra el prompt
        """
        prompt = db.query(PromptTemplateModel).filter(
            PromptTemplateModel.id == prompt_id
        ).first()
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt template con ID {prompt_id} no encontrado"
            )
        
        # Actualizar solo los campos que vienen en el request
        update_data = prompt_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(prompt, field, value)
        
        db.commit()
        db.refresh(prompt)
        
        return PromptTemplateResponse.model_validate(prompt)
    
    @staticmethod
    def deactivate_prompt_template(
        db: Session,
        prompt_id: int
    ) -> PromptTemplateResponse:
        """
        Desactiva un prompt template.
        
        Args:
            db: Sesión de base de datos
            prompt_id: ID del prompt a desactivar
            
        Returns:
            PromptTemplateResponse con el prompt desactivado
            
        Raises:
            HTTPException 404: Si no se encuentra el prompt
        """
        prompt = db.query(PromptTemplateModel).filter(
            PromptTemplateModel.id == prompt_id
        ).first()
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt template con ID {prompt_id} no encontrado"
            )
        
        prompt.activo = False
        db.commit()
        db.refresh(prompt)
        
        return PromptTemplateResponse.model_validate(prompt)
    
    @staticmethod
    def activate_prompt_template(
        db: Session,
        prompt_id: int
    ) -> PromptTemplateResponse:
        """
        Activa un prompt template y desactiva todos los demás.
        
        Args:
            db: Sesión de base de datos
            prompt_id: ID del prompt a activar
            
        Returns:
            PromptTemplateResponse con el prompt activado
            
        Raises:
            HTTPException 404: Si no se encuentra el prompt
        """
        prompt = db.query(PromptTemplateModel).filter(
            PromptTemplateModel.id == prompt_id
        ).first()
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt template con ID {prompt_id} no encontrado"
            )
        
        # Desactivar todos los prompts
        db.query(PromptTemplateModel).update({"activo": False})
        
        # Activar el prompt seleccionado
        prompt.activo = True
        db.commit()
        db.refresh(prompt)
        
        return PromptTemplateResponse.model_validate(prompt)
    
    @staticmethod
    def delete_prompt_template(
        db: Session,
        prompt_id: int
    ) -> dict:
        """
        Elimina un prompt template (hard delete).
        
        Args:
            db: Sesión de base de datos
            prompt_id: ID del prompt a eliminar
            
        Returns:
            dict con mensaje de confirmación
            
        Raises:
            HTTPException 404: Si no se encuentra el prompt
            HTTPException 400: Si el prompt está activo
        """
        prompt = db.query(PromptTemplateModel).filter(
            PromptTemplateModel.id == prompt_id
        ).first()
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prompt template con ID {prompt_id} no encontrado"
            )
        
        if prompt.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un prompt activo. Desactívalo primero."
            )
        
        db.delete(prompt)
        db.commit()
        
        return {"message": f"Prompt template {prompt_id} eliminado exitosamente"}