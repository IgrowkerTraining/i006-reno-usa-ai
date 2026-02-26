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

class AnalisisIAEsperado(BaseModel):
    general_project_status: str
    execution_schedule_analysis: str
    safety_compliance_analysis: str
    technical_approvals_analysis: str
    overall_observation: str
    risk_level: str
    detected_inconsistencies: list[str]

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
    

    async def analizar_obra(self, snapshot_data: dict, modelo: str = "arcee-ai/trinity-large-preview:free") -> dict:
        """
        Envía el snapshot de la obra a la IA y fuerza una respuesta en formato JSON estricto.
        Devuelve el análisis y las métricas de consumo de OpenRouter.
        """
        prompt_sistema = """
        Eres un auditor experto en obras de construcción. 
        Analiza el siguiente snapshot de datos de un proyecto y devuelve ÚNICAMENTE un objeto JSON válido.
        El JSON debe cumplir ESTRICTAMENTE con esta estructura (sin texto extra, sin saludos, sin bloques markdown de código):
        {
            "general_project_status": "texto descriptivo",
            "execution_schedule_analysis": "texto descriptivo",
            "safety_compliance_analysis": "texto descriptivo",
            "technical_approvals_analysis": "texto descriptivo",
            "overall_observation": "observación general detallada que obligatoriamente DEBE TENER MÁS DE 50 CARACTERES.",
            "risk_level": "low", "medium" o "high",
            "detected_inconsistencies": ["inconsistencia 1"] o [] si no hay
        }
        """

        payload = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Snapshot de la obra:\n{json.dumps(snapshot_data, indent=2)}"}
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
                
            # 2. Validar ESTRUCTURA (Si falta un campo, Pydantic tira ValidationError)
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
                }
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
