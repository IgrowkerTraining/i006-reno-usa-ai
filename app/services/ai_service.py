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
            
            try:
                analisis_json = json.loads(clean_content)
                logger.info("Análisis de obra parseado exitosamente.")
            except json.JSONDecodeError:
                error_msg = f"La IA no devolvió un JSON válido. Respuesta: {raw_content}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            costo_total = (tokens_entrada * 0.0001) + (tokens_salida * 0.0002)

            return {
                "analisis": analisis_json,
                "modelo_utilizado": modelo_real,
                "metricas": {
                    "tokens_entrada": tokens_entrada,
                    "tokens_salida": tokens_salida,
                    "tiempo_ejecucion_ms": tiempo_ejecucion,
                    "costo_estimado": costo_total,
                    "status_code": response.status_code
                }
            }

        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter API error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error general llamando a OpenRouter: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)


    async def list_models(self) -> List[ModelInfo]:
        """List available models from OpenRouter."""
        # ... (código original intacto)
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
