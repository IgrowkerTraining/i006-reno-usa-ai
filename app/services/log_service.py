from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models.log_peticion import LogPeticionDB

class LogService:
    def __init__(self, db: Session):
        self.db = db

    def registrar_metrica_ia(self, status_code: int, reporte_id: UUID = None, tokens_entrada: int = None, tokens_salida: int = None, costo_estimado: float = None, tiempo_ejecucion_ms: int = None):
        """
        Guarda las métricas de consumo y tiempo de la petición a OpenRouter.
        """
        nuevo_log = LogPeticionDB(
            reporte_id=reporte_id,
            tokens_entrada=tokens_entrada,
            tokens_salida=tokens_salida,
            costo_estimado=costo_estimado,
            tiempo_ejecucion_ms=tiempo_ejecucion_ms,
            status_code=status_code
        )
        self.db.add(nuevo_log)
        self.db.commit()
        self.db.refresh(nuevo_log)
        return nuevo_log
    
    def obtener_metrica_por_reporte(self, reporte_id: UUID):
        """
        Busca el log exacto de consumo para un reporte específico.
        """
        return self.db.query(LogPeticionDB).filter(LogPeticionDB.reporte_id == reporte_id).first()

    def obtener_metricas(self, limite: int = 50):
        return self.db.query(LogPeticionDB).order_by(LogPeticionDB.fecha_evento.desc()).limit(limite).all()