from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

class LogPeticionDB(Base):
    __tablename__ = "log_peticiones"

    # Según el DER, este ID es un BigInt, no un UUID
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Lo conectamos con el reporte (dejamos el nullable=True por si la IA falla ANTES de crear el reporte)
    reporte_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Métricas de consumo de la IA
    tokens_entrada = Column(Integer, nullable=True)
    tokens_salida = Column(Integer, nullable=True)
    costo_estimado = Column(Numeric(10, 6), nullable=True) # Permite 4 enteros y 6 decimales
    
    # Rendimiento
    tiempo_ejecucion_ms = Column(Integer, nullable=True)
    status_code = Column(Integer, nullable=False) # 200 si anduvo joya, 500 si falló la IA, etc.
    
    fecha_evento = Column(DateTime, default=datetime.utcnow, index=True)