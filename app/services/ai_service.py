"""AI service for OpenRouter integration."""

import httpx
import uuid
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.config.settings import settings
from app.models.schemas import ChatRequest, ChatResponse, ModelInfo
from app.core.logging import get_logger
from app.core.security import mask_api_key
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from app.services.prompt_template_service import PromptTemplateService

class AnalisisIAEsperado(BaseModel):
    advancePercentage: int
    completedTasksCount: int
    uncompletedTasksCount: int
    inProcessTasks: list[str]
    safetyPercent: int
    safetyCount: int
    electricalPercent: int
    electricalCount: int
    correctionPercent: int
    correctionCount: int

logger = get_logger(__name__)


class AIService:
    """Service for interacting with OpenRouter API."""
    
    def __init__(self):
        """Initialize the AI service."""
        self.client = httpx.AsyncClient(
            base_url=settings.openrouter_base_url,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-username/template-python-fastapi",
                "X-Title": settings.app_name,
            },
            timeout=60.0
        )
        logger.info(f"AI Service initialized with API key: {mask_api_key(settings.openrouter_api_key)}")
    
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """Create a chat completion using OpenRouter API."""
        # ... (código original intacto)
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        payload = {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stream": request.stream,
        }
        
        try:
            logger.info(f"Sending chat completion request for model: {request.model}")
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            chat_response = ChatResponse(
                id=data.get("id", str(uuid.uuid4())),
                created=data.get("created", int(datetime.now().timestamp())),
                model=data.get("model", request.model),
                choices=data.get("choices", []),
                usage=data.get("usage")
            )
            
            logger.info(f"Chat completion successful: {chat_response.id}")
            return chat_response
            
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter API error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error calling OpenRouter API: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    

    async def analizar_obra(self, snapshot_data: dict, db: Session, modelo: str = "arcee-ai/trinity-large-preview:free") -> dict:
        """
        Envía el snapshot de la obra a la IA usando el prompt dinámico de la BD.
        Devuelve el análisis y las métricas de consumo de OpenRouter.
        """
        
        # 1. Buscamos el prompt activo (las reglas) en la base de datos
        prompt_activo = PromptTemplateService.get_active_prompt(db)
        
        if not prompt_activo:
            raise ValueError("No hay ningún prompt activo en la base de datos. Por favor, crea uno primero.")
            
        prompt_sistema = prompt_activo.template_text
        version_usada = prompt_activo.version

        # --- 2. NUEVO: MASTICAMOS LOS DATOS ANTES DE ENVIARLOS ---
        tasks = snapshot_data.get("tasks_snapshot", [])
        active_phase = snapshot_data.get("active_phase", "")
        project_name = snapshot_data.get("project_name", "")

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
        pending_tasks = total_tasks - completed_tasks

        in_process_task_names = [
            t.get("name") for t in tasks 
            if t.get("phase") == active_phase and t.get("status") != "completed"
        ]

        safety_count = sum(1 for t in tasks if t.get("is_incidence") is True and t.get("category") == "SAFETY")
        electrical_count = sum(1 for t in tasks if t.get("is_incidence") is True and t.get("category") == "ELECTRICAL")
        correction_count = sum(1 for t in tasks if t.get("is_incidence") is True and t.get("category") == "CORRECTION")

        datos_procesados = {
            "project_name": project_name,
            "active_phase": active_phase,
            "PRE_CALCULATED_METRICS": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "pending_tasks": pending_tasks,
                "in_process_task_names": in_process_task_names,
                "incidences": {
                    "safety_count": safety_count,
                    "electrical_count": electrical_count,
                    "correction_count": correction_count
                }
            }
        }
        # ---------------------------------------------------------

        # 3. Armamos el payload con los datos_procesados en lugar del snapshot_data
        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Métricas calculadas de la obra:\n{json.dumps(datos_procesados, indent=2)}"}
            ]
        }

        inicio_ms = time.time()
        
        try:
            logger.info(f"Enviando snapshot de obra a OpenRouter (modelo: {modelo})")
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            fin_ms = time.time()
            tiempo_ejecucion = int((fin_ms - inicio_ms) * 1000)

            data = response.json()
            modelo_real = data.get("model", modelo)
            tokens_entrada = data.get("usage", {}).get("prompt_tokens", 0)
            tokens_salida = data.get("usage", {}).get("completion_tokens", 0)
            
            raw_content = data["choices"][0]["message"]["content"]
            clean_content = raw_content.strip().strip("```json").strip("```").strip()
            
            # 1. Validar que sea JSON
            try:
                analisis_raw = json.loads(clean_content)
            except json.JSONDecodeError:
                raise ValueError("La IA no devolvió un formato JSON válido.")
                
            # 2. Validar ESTRUCTURA
            try:
                analisis_validado = AnalisisIAEsperado(**analisis_raw).model_dump()
            except ValidationError as e:
                logger.error(f"Estructura incorrecta de la IA: {e}")
                raise ValueError(f"La IA omitió campos o inventó nuevos. Detalle: {e.error_count()} errores encontrados.")

            costo_total = (tokens_entrada * 0.0001) + (tokens_salida * 0.0002)

            return {
                "analisis": analisis_validado,
                "modelo_utilizado": modelo_real,
                "metricas": {
                    "tokens_entrada": tokens_entrada,
                    "tokens_salida": tokens_salida,
                    "tiempo_ejecucion_ms": tiempo_ejecucion,
                    "costo_estimado": costo_total,
                    "status_code": response.status_code
                },
                "prompt_version_id": version_usada
            }

        # --- MANEJO DE ERRORES EXTERNOS ---
        except httpx.TimeoutException:
            logger.error("OpenRouter tardó demasiado en responder.")
            raise RuntimeError("Timeout: El servicio de IA tardó demasiado en responder.")
            
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 402:
                raise RuntimeError("Sin saldo: La cuenta de OpenRouter no tiene créditos suficientes.")
            elif status == 429:
                raise RuntimeError("Rate Limit: Demasiadas peticiones a OpenRouter. Intente más tarde.")
            else:
                raise RuntimeError(f"Error en OpenRouter ({status}): {e.response.text}")
                
        except httpx.RequestError as e:
            logger.error(f"Error de red contactando a OpenRouter: {e}")
            raise RuntimeError("Error de red: No se pudo conectar con el servicio de IA.")

    async def list_models(self) -> List[ModelInfo]:
        """List available models from OpenRouter."""
        try:
            logger.info("Fetching available models from OpenRouter")
            response = await self.client.get("/models")
            response.raise_for_status()
            
            data = response.json()
            models_data = data.get("data", [])
            
            models = [
                ModelInfo(
                    id=model.get("id", ""),
                    name=model.get("name"),
                    description=model.get("description"),
                    pricing=model.get("pricing")
                )
                for model in models_data
            ]
            
            logger.info(f"Retrieved {len(models)} models")
            return models
            
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter API error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error fetching models: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def health_check(self) -> bool:
        """Check if the AI service is healthy."""
        try:
            await self.list_models()
            return True
        except Exception as e:
            logger.error(f"AI service health check failed: {str(e)}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        logger.info("AI service client closed")

# Global AI service instance
ai_service = AIService()
