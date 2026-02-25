from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db

from app.models.reporte_generado import GenerateAnalysisRequest, ReporteGeneradoResponse

from app.services.reporte_service import ReporteService


router = APIRouter(prefix="/reportes", tags=["Reportes Generados"])


@router.post("/", response_model=ReporteGeneradoResponse)
def crear_reporte_analisis(
    request: GenerateAnalysisRequest, 
    db: Session = Depends(get_db)
):
    """
    Recibe un snapshot, lo analiza con IA (simulado por ahora), y lo guarda en la BD.
    """
    servicio = ReporteService(db)
    
    try:
        # ACA IRÍA LA LLAMADA A EL SERVICIO DE IA (OpenRouter)
        analisis_simulado = {
            "general_project_status": "El proyecto avanza según lo esperado en la fase actual.",
            "execution_schedule_analysis": "Desviación menor, pero dentro del margen histórico aceptable.",
            "safety_compliance_analysis": "Se reportan medidas de seguridad y pólizas activas.",
            "technical_approvals_analysis": "Aprobación técnica vigente sin discrepancias.",
            "overall_observation": "El proyecto se encuentra estable, con un riesgo operativo bajo y sin problemas críticos a la vista en esta fase de la obra.", # 👈 ESTA ES LA LÍNEA NUEVA
            "detected_inconsistencies": [],
            "risk_level": "low"
        }
        
        # Usamos tu ReporteService para guardarlo en PostgreSQL
        nuevo_reporte = servicio.guardar_reporte(
            project_id=request.snapshot.project_code,       
            fase_analizada=request.snapshot.current_phase,  
            input_snapshot=request.model_dump(mode='json'),          
            output_analisis=analisis_simulado,
            modelo_utilizado="arcee-ai/trinity-large-preview:free",
            prompt_version_id=1 
        )
        
        return nuevo_reporte
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el reporte: {str(e)}")


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