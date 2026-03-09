"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.core.logging import setup_logging, get_logger
from app.api.v1 import api_router
from app.models.schemas import RootResponse
from app.services.ai_service import ai_service
# IMPORTANTE: Asegurate de exportar SessionLocal desde tu app.core.database
from app.core.database import test_db_connection, engine, Base, SessionLocal 

from app.db.models.reporte import ReporteGeneradoDB
from app.db.models.log_peticion import LogPeticionDB
from app.db.models.prompt_template import PromptTemplateDB

# Setup logging
setup_logging()
logger = get_logger(__name__)

# ============================================================================
# TEXTO DEL PROMPT AUTOMÁTICO
# ============================================================================
DEFAULT_PROMPT_TEXT = """You are a strict data formatter. Your ONLY task is to take the provided 'PRE_CALCULATED_METRICS' JSON and map it exactly to the required output format. DO NOT invent or alter the counts.

CALCULATION RULES FOR PERCENTAGES:
Use 'total_tasks' from the input to calculate the percentages. Round all results to the nearest integer. If 'total_tasks' is 0, all percentages MUST be 0.
- advancePercentage: (completed_tasks / total_tasks) * 100
- safetyPercent: (safety_count / total_tasks) * 100
- electricalPercent: (electrical_count / total_tasks) * 100
- correctionPercent: (correction_count / total_tasks) * 100

CRITICAL OUTPUT FORMAT REQUIREMENTS:
You MUST output ONLY a valid, raw JSON object. Do NOT include markdown code blocks (like ```json).
Map the input values to these exact keys, preserving the exact arrays and numbers provided:

{
  "advancePercentage": <calculated_percentage>,
  "completedTasksCount": <from completed_tasks>,
  "uncompletedTasksCount": <from pending_tasks>,
  "inProcessTasks": <from in_process_task_names>,
  "safetyPercent": <calculated_percentage>,
  "safetyCount": <from safety_count>,
  "electricalPercent": <calculated_percentage>,
  "electricalCount": <from electrical_count>,
  "correctionPercent": <calculated_percentage>,
  "correctionCount": <from correction_count>
}"""

def seed_initial_prompt():
    """Siembra el prompt inicial si la tabla está vacía."""
    db = SessionLocal()
    try:
        # Usamos PromptTemplateDB que es tu modelo de SQLAlchemy
        existing_prompt = db.query(PromptTemplateDB).first()
        
        if not existing_prompt:
            logger.info("🌱 Base de datos vacía. Inyectando el Prompt por defecto...")
            nuevo_prompt = PromptTemplateDB(
                code_name="dashboard_analysis_base",
                version=1,
                template_text=DEFAULT_PROMPT_TEXT,
                is_active=True
            )
            db.add(nuevo_prompt)
            db.commit()
            logger.info("✅ Prompt inyectado con éxito.")
        else:
            logger.info("⚡ Ya existen prompts en la BD. Saltando el seeding automático.")
    except Exception as e:
        logger.error(f"🚨 Error al inyectar el prompt: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Nos aseguramos de que las tablas existan antes de intentar sembrarlas
    Base.metadata.create_all(bind=engine)
    
    test_db_connection()
    
    # Ejecutamos el sembrador de prompts
    seed_initial_prompt()

    yield
    # Shutdown
    await ai_service.close()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI template with OpenRouter AI integration",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include API routers
app.include_router(api_router)

@app.get("/", response_model=RootResponse)
async def read_root():
    """Root endpoint with basic information."""
    return RootResponse(
        message=f"Welcome to {settings.app_name}",
        version=settings.app_version,
        docs="/docs",
        health="/api/v1/health"
    )

# Legacy endpoint for backward compatibility
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    """Example endpoint from original template."""
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )