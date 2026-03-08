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

    def obtener_ultimo_reporte(self, project_id: str):
        #funcion para obtener reporte mas reciente#
        return (
            self.db.query(ReporteGeneradoDB).filter(ReporteGeneradoDB.project_id == project_id).order_by(ReporteGeneradoDB.fecha_generacion.desc()).first()
        )
    
    def comparar_snapshot(self, snapshot_viejo: dict, snapshot_nuevo: dict) -> bool:
        camposIgnorar={'period_start', 'period_end'}

        viejo_limpio = {k: v for k, v in snapshot_viejo.items() if k not in camposIgnorar}
        nuevo_limpio = {k: v for k, v in snapshot_nuevo.items() if k not in camposIgnorar}

        return viejo_limpio == nuevo_limpio
    
    def guardar_reporte_con_cache(
        self, 
        project_id: str, 
        fase_analizada: str, 
        input_snapshot: dict, 
        output_analisis: dict, 
        modelo_utilizado: str, 
        prompt_version_id: int
    ):
        """Guarda reporte solo si snapshot cambió, sino devuelve caché."""
        
        # 1. Buscar último reporte
        ultimo_reporte = self.obtener_ultimo_reporte(project_id)
        
        # 2. Si existe, comparar
        if ultimo_reporte:
            if self.snapshots_son_iguales(ultimo_reporte.input_snapshot, input_snapshot):
                # ✨ CACHÉ HIT
                return {
                    "reporte": ultimo_reporte,
                    "es_cache": True,
                    "mensaje": "Snapshot sin cambios"
                }
        
        # 3. Generar nuevo
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
        
        return {
            "reporte": nuevo_reporte,
            "es_cache": False,
            "mensaje": "Análisis generado"
        }

      