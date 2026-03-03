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
    """Estructura interna del análisis generado por la IA."""
    general_project_status: str = Field(..., description="Resumen del estado general del proyecto")
    execution_schedule_analysis: str = Field(..., description="Análisis del cronograma y desviaciones")
    safety_compliance_analysis: str = Field(..., description="Evaluación de medidas de seguridad")
    technical_approvals_analysis: str = Field(..., description="Estado de aprobaciones técnicas")
    overall_observation: str = Field(..., min_length=50, description="Observación detallada (min 50 caracteres)")
    risk_level: str = Field(..., pattern="^(low|medium|high)$", description="Nivel de riesgo detectado")
    detected_inconsistencies: List[str] = Field(default_factory=list, description="Lista de inconsistencias halladas")

class ReporteLimpioResponse(BaseModel):
    id: UUID
    analisis: AnalisisIA

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "302bf0d6-2eb0-4b9f-bf57-1e9f9c1fab84",
                "analisis": {
                    "general_project_status": "Project at 80% completion...",
                    "execution_schedule_analysis": "1-day delay due to logistics...",
                    "safety_compliance_analysis": "All PPE standards are being met...",
                    "technical_approvals_analysis": "Licensed architect approval confirmed...",
                    "overall_observation": "The project is advancing well according to the schedule and safety standards.",
                    "risk_level": "low",
                    "detected_inconsistencies": []
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
        # 1. Llamamos a la IA pasándole el JSON puro de la obra
        resultado_ia = await ai_service.analizar_obra(
            snapshot_data=request.snapshot.model_dump(mode='json'),
            db=db
        )
        
        # 2. Guardamos en BD el reporte con la respuesta REAL de la IA
        rep_servicio = ReporteService(db)
        nuevo_reporte = rep_servicio.guardar_reporte(
            project_id=request.snapshot.project_code,       
            fase_analizada=request.snapshot.current_phase,  
            input_snapshot=request.model_dump(mode='json'),
            output_analisis=resultado_ia["analisis"],
            modelo_utilizado=resultado_ia["modelo_utilizado"],
            prompt_version_id=resultado_ia["prompt_version_id"] 
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

        # 4. Devolvemos la respuesta que ahora FastAPI validará contra el modelo
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