from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class PromptTemplateDB(Base):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    code_name = Column(String(100), nullable=False)          
    version = Column(Integer, nullable=False)
    template_text = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)                 
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 