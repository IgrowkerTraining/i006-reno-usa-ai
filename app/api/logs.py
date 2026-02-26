from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.log_service import LogService

router = APIRouter(prefix="/logs", tags=["Métricas de IA"])

@router.get(
    "/",
    summary="Listar métricas de consumo de la IA",
    description="""
    Devuelve un historial paginado con las métricas de uso del motor de Inteligencia Artificial (OpenRouter).
    
    **Datos incluidos:**
    * Cantidad de tokens consumidos (Entrada y Salida).
    * Costo estimado en USD.
    * Tiempo de respuesta de la IA (milisegundos).
    * Referencia directa al ID del reporte generado.
    """,
    response_description="Una lista de objetos con las métricas de cada petición."
)
def listar_metricas(limite: int = 50, db: Session = Depends(get_db)):
    """
    Devuelve las últimas métricas de consumo de tokens y tiempos de respuesta de la IA.
    """
    servicio = LogService(db)
    return servicio.obtener_metricas(limite=limite)