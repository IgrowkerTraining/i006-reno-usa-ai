"""
Schemas for Prompt Templates
Management of versioned prompt templates
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class PromptTemplateBase(BaseModel):
    code_name: str = Field(..., min_length=1, max_length=100) 
    version: int = Field(..., ge=1)
    template_text: str = Field(..., min_length=10)
    is_active: bool = Field(default=True)                    

class PromptTemplateCreate(PromptTemplateBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code_name": "auditor_base",
                "version": 1,
                "template_text": "You are an expert construction...",
                "is_active": True
            }
        }
    )

class PromptTemplateUpdate(BaseModel):
    template_text: Optional[str] = Field(None, min_length=10)
    is_active: Optional[bool] = Field(None)

class PromptTemplateResponse(PromptTemplateBase):
    id: int
    created_at: datetime                                   
    model_config = ConfigDict(from_attributes=True)

class PromptTemplateListItem(BaseModel):
    id: int
    code_name: str
    version: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ActivePromptResponse(BaseModel):
    id: int
    code_name: str
    version: int
    template_text: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)