from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from app.core.database import Base


class PromptTemplateModel(Base):
    """
    Modelo de base de datos para prompts_templates.
    Almacena las plantillas de prompts versionadas para el análisis de IA.
    """
    
    __tablename__ = "prompts_templates"
    
    # Columnas según tu DER
    id = Column(
        Integer, 
        primary_key=True, 
        autoincrement=True,
        comment="ID único del prompt template"
    )
    
    nombre_codigo = Column(
        String(100), 
        nullable=False,
        unique=True,
        index=True,
        comment="Código único identificador del prompt"
    )
    
    version = Column(
        Integer, 
        nullable=False,
        comment="Número de versión del prompt"
    )
    
    template_text = Column(
        Text, 
        nullable=False,
        comment="Texto completo del template del prompt"
    )
    
    activo = Column(
        Boolean, 
        default=True,
        nullable=False,
        index=True,
        comment="Indica si esta versión está activa"
    )
    
    fecha_creacion = Column(
        DateTime, 
        default=datetime.utcnow,
        nullable=False,
        comment="Fecha y hora de creación del template"
    )
    
    def __repr__(self):
        return f"<PromptTemplate(id={self.id}, codigo='{self.nombre_codigo}', version={self.version}, activo={self.activo})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            "id": self.id,
            "nombre_codigo": self.nombre_codigo,
            "version": self.version,
            "template_text": self.template_text,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
