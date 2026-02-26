from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db

from app.models.reporte_generado import GenerateAnalysisRequest, ReporteGeneradoResponse

from app.services.reporte_service import ReporteService

from app.services.log_service import LogService

from app.services.ai_service import ai_service


router = APIRouter(prefix="/reportes", tags=["Reportes Generados"])

@router.post(
    "/", 
    response_model=ReporteGeneradoResponse,
    summary="Generar y guardar un nuevo análisis de obra",
    description="""
    Recibe un **Snapshot** (la foto actual) con los datos de una obra en curso. 
    Envía estos datos a la IA (por ahora) para analizar métricas, detectar riesgos y validar tiempos.
    Finalmente, guarda todo el registro (entrada y salida) en la base de datos PostgreSQL 
    y registra automáticamente el consumo de tokens en el log del sistema.
    """,
    response_description="El reporte guardado con su UUID y el análisis de la IA."
)
async def crear_reporte_analisis(
    request: GenerateAnalysisRequest, 
    db: Session = Depends(get_db)
):
    """
    Recibe un snapshot, lo analiza con IA, y lo guarda en la BD.
    """
    servicio = ReporteService(db)
    
    try:
        # 1. Llamamos a la IA pasándole el JSON puro de la obra
        resultado_ia = await ai_service.analizar_obra(
            snapshot_data=request.snapshot.model_dump(mode='json'),
        )
        
        # 2. Guardamos en BD el reporte con la respuesta REAL de la IA
        rep_servicio = ReporteService(db)
        nuevo_reporte = rep_servicio.guardar_reporte(
            project_id=request.snapshot.project_code,       
            fase_analizada=request.snapshot.current_phase,  
            input_snapshot=request.model_dump(mode='json'), 
            output_analisis=resultado_ia["analisis"],
            modelo_utilizado=resultado_ia["modelo_utilizado"],
            prompt_version_id=1 
        )

        # 3. Guardamos los logs reales de consumo y tiempo
        log_servicio = LogService(db)
        metricas = resultado_ia["metricas"]
        log_servicio.registrar_metrica_ia(
            status_code=metricas["status_code"],
            reporte_id=nuevo_reporte.id, 
            tokens_entrada=metricas["tokens_entrada"],
            tokens_salida=metricas["tokens_salida"],
            costo_estimado=metricas["costo_estimado"],
            tiempo_ejecucion_ms=metricas["tiempo_ejecucion_ms"]
        )

        return nuevo_reporte

    except ValueError as ve:
        # Si la IA falló formateando el JSON, lo avisamos con un error 422
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Si algo más explota, guardamos un log fallido por las dudas
        log_servicio = LogService(db)
        log_servicio.registrar_metrica_ia(status_code=500, tiempo_ejecucion_ms=0)
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/{reporte_id}", response_model=ReporteGeneradoResponse)
def obtener_reporte(
    reporte_id: UUID, 
    db: Session = Depends(get_db)
):
    """
    Busca un reporte específico en la base de datos usando su ID.
    """
    servicio = ReporteService(db)
    reporte = servicio.obtener_reporte(reporte_id)
    
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
        
    return reporte