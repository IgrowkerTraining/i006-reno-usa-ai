from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.log_service import LogService

router = APIRouter(prefix="/logs", tags=["Métricas de IA"])

@router.get("/")
def listar_metricas(limite: int = 50, db: Session = Depends(get_db)):
    """
    Devuelve las últimas métricas de consumo de tokens y tiempos de respuesta de la IA.
    """
    servicio = LogService(db)
    return servicio.obtener_metricas(limite=limite)