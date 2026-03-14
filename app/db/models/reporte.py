import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

class ReporteGeneradoDB(Base):
    __tablename__ = "reportes_generados"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    #ID del proyecto al que corresponde el reporte
    project_id = Column(String, nullable=False, index=True)
    fase_analizada = Column(String, nullable=False)
    
    #Snapshot de la entrada y salida del modelo, para poder analizarla posteriormente
    input_snapshot = Column(JSONB, nullable=False)
    output_analisis = Column(JSONB, nullable=False)
    
    #Modelo ia utilizado para generar el reporte
    modelo_utilizado = Column(String, nullable=False)
    
    #ID del template de prompt utilizado para generar el reporte
    
    #Descomentar la siguiente línea y comentar la anterior si se quiere establecer una relación con la tabla de templates de prompt
    prompt_version_id = Column(Integer, nullable=False)
    #prompt_version_id = Column(Integer, ForeignKey("prompts_templates.id"), nullable=False)
    
    #fecha de generación del reporte
    fecha_generacion = Column(DateTime, default=datetime.utcnow)