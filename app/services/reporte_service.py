from sqlalchemy.orm import Session
from uuid import UUID

from app.db.models.reporte import ReporteGeneradoDB

class ReporteService:
    def __init__(self, db: Session):
        """
        Al instanciar el servicio, le pasamos la sesión abierta de la base de datos.
        """
        self.db = db

    def guardar_reporte(self, project_id: str, fase_analizada: str, input_snapshot: dict, output_analisis: dict, modelo_utilizado: str, prompt_version_id: int):
        """
        Guarda un nuevo reporte de análisis en la base de datos.
        """

        nuevo_reporte = ReporteGeneradoDB(
            project_id=project_id,
            fase_analizada=fase_analizada,
            input_snapshot=input_snapshot, 
            output_analisis=output_analisis,
            modelo_utilizado=modelo_utilizado,
            prompt_version_id=prompt_version_id
        )
        
        self.db.add(nuevo_reporte)
        
        self.db.commit()
        
        self.db.refresh(nuevo_reporte)
        
        return nuevo_reporte

    def obtener_reporte(self, reporte_id: UUID):
        """
        Busca un reporte específico usando su UUID.
        """
        return self.db.query(ReporteGeneradoDB).filter(ReporteGeneradoDB.id == reporte_id).first()

    def listar_reportes_por_proyecto(self, project_id: str):
        """
        Trae todos los reportes de una obra en particular.
        """
        return self.db.query(ReporteGeneradoDB).filter(ReporteGeneradoDB.project_id == project_id).all()