from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.core.database import Base

class PromptTemplateDB(Base):
    """Modelo de base de datos para prompts_templates."""
    __tablename__ = "prompts_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_codigo = Column(String(100), nullable=False, unique=True, index=True)
    version = Column(Integer, nullable=False)
    template_text = Column(Text, nullable=False)
    activo = Column(Boolean, default=True, nullable=False, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)