from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import List

from app.core.database import get_db
from app.models.reporte_generado import GenerateAnalysisRequest, ReporteGeneradoResponse
from app.services.reporte_service import ReporteService
from app.services.log_service import LogService
from app.services.ai_service import ai_service

class AnalisisIA(BaseModel):
    """Mathematical structure to feed the General Analysis Dashboard."""
    
    # Progress Metrics
    advancePercentage: int = Field(..., description="Integer percentage of overall progress (completed tasks / total tasks) * 100. Returns 0 if there are no tasks.")
    completedTasksCount: int = Field(..., description="Total absolute count of completed tasks in the project.")
    uncompletedTasksCount: int = Field(..., description="Total absolute count of uncompleted tasks (pending or in_progress) in the project.")
    
    # Active Phase details
    inProcessTasks: List[str] = Field(default_factory=list, description="List of names of the tasks that are 'pending' or 'in_progress' specifically in the currently active phase.")
    
    # Incidence Metrics (Percentages and absolute counts)
    safetyPercent: int = Field(..., description="Integer percentage of SAFETY incidences over the total number of tasks.")
    safetyCount: int = Field(..., description="Total absolute count of active SAFETY incidences.")
    
    electricalPercent: int = Field(..., description="Integer percentage of ELECTRICAL incidences over the total number of tasks.")
    electricalCount: int = Field(..., description="Total absolute count of active ELECTRICAL incidences.")
    
    correctionPercent: int = Field(..., description="Integer percentage of CORRECTION incidences over the total number of tasks.")
    correctionCount: int = Field(..., description="Total absolute count of active CORRECTION incidences.")

class ReporteLimpioResponse(BaseModel):
    id: UUID
    analisis: AnalisisIA

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "302bf0d6-2eb0-4b9f-bf57-1e9f9c1fab84",
                "analisis": {
                    "advancePercentage": 65,
                    "completedTasksCount": 65,
                    "uncompletedTasksCount": 35,
                    "inProcessTasks": [
                        "Project Planning", 
                        "Electrical Installation", 
                        "Plumber registration"
                    ],
                    "safetyPercent": 3,
                    "safetyCount": 2,
                    "electricalPercent": 3,
                    "electricalCount": 2,
                    "correctionPercent": 3,
                    "correctionCount": 2
                }
            }
        }
    )

router = APIRouter(prefix="/reportes", tags=["Reportes Generados"])

@router.post(
    "/", 
    response_model=ReporteLimpioResponse,
    summary="Generar y guardar un nuevo análisis de obra",
    description="""
    Recibe un **Snapshot** de obra, lo analiza con IA usando el prompt activo, 
    guarda el registro en PostgreSQL y devuelve una respuesta limpia con el ID y el análisis.
    """,
    response_description="El UUID del reporte y el análisis detallado de la IA."
)
async def crear_reporte_analisis(
    request: GenerateAnalysisRequest, 
    db: Session = Depends(get_db)
):
    """
    Recibe un snapshot, lo analiza con IA, lo guarda en la BD y devuelve una respuesta limpia.
    """
    try:
        rep_servicio = ReporteService(db)
        
        # Verificar si existe un reporte anterior para este proyecto
        # 1. BÚSQUEDA EN CACHÉ: Buscamos por el ID único
        ultimo_reporte = rep_servicio.obtener_ultimo_reporte(request.snapshot.project_id)
        
        if ultimo_reporte:
            # Extraer el snapshot del input_snapshot guardado
            snapshot_viejo = ultimo_reporte.input_snapshot.get('snapshot', {})
            snapshot_nuevo = request.snapshot.model_dump(mode='json')
            
            # Comparar snapshots
            if rep_servicio.snapshots_son_iguales(snapshot_viejo, snapshot_nuevo):
                # Devolver análisis guardado sin generar uno nuevo
                return {
                    "id": ultimo_reporte.id,
                    "analisis": ultimo_reporte.output_analisis
                }
        
        # Generar nuevo análisis si no existe reporte previo o si el snapshot cambió
        resultado_ia = await ai_service.analizar_obra(
            snapshot_data=request.snapshot.model_dump(mode='json'),
            db=db
        )
        
        # 2. GUARDADO: Guardamos usando el ID único
        nuevo_reporte = rep_servicio.guardar_reporte(
            project_id=request.snapshot.project_id,
            fase_analizada=request.snapshot.active_phase, 
            input_snapshot=request.model_dump(mode='json'),
            output_analisis=resultado_ia["analisis"],
            modelo_utilizado=resultado_ia["modelo_utilizado"],
            prompt_version_id=resultado_ia["prompt_version_id"] 
        )

        # Registrar métricas de la petición
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

        return {
            "id": nuevo_reporte.id,
            "analisis": nuevo_reporte.output_analisis
        }

    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except RuntimeError as re:
        log_servicio = LogService(db)
        log_servicio.registrar_metrica_ia(status_code=502, tiempo_ejecucion_ms=0)
        raise HTTPException(status_code=502, detail=str(re))
    except Exception as e:
        log_servicio = LogService(db)
        log_servicio.registrar_metrica_ia(status_code=500, tiempo_ejecucion_ms=0)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")


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