# Documentación de la API  - Reno USA AI Backend

Esta documentación detalla los endpoints disponibles para la generación de reportes de obra impulsados por Inteligencia Artificial y el monitoreo de su rendimiento.

**Base URL:** `http://localhost:8000/api/v1`

---

## 1. Reportes Generados

### `POST /reportes/`
**Descripción:** Recibe un snapshot con el estado actual de una obra, lo envía al motor de IA (OpenRouter) para su evaluación técnica, y guarda el resultado junto con el contexto en la tabla `reportes_generados`.

**Request Body (JSON):**
Espera un objeto que contenga el `snapshot` detallado de la obra y el nombre del template de prompt a utilizar.

{
  "snapshot": {
    "current_phase": "Interior framing",
    "location": "Montecito, California",
    "project_code": "RENO-US-2026-009",
    "phase_completion_percentage": 60,
    "schedule_deviation_days": 1,
    "supervisor_notes": "Minor delay due to material delivery",
    "safety_measures": ["Hard hats and PPE enforced"],
    "tasks_performed": ["Drywall installation"]
  },
  "prompt_template_name": "auditor_base"
}

**Respuesta Exitosa (200 OK):**
Devuelve el registro completo guardado en la base de datos, incluyendo el ID único generado (`id`), el ID del proyecto (`project_id`), el snapshot de entrada (`input_snapshot`), el análisis estructurado devuelto por la IA (`output_analisis`), y el modelo exacto que procesó la petición (`modelo_utilizado`).

{
  "id": "f34ef4ca-ea94-457c-9f68-907980c30e1e",
  "project_id": "RENO-US-2026-009",
  "fase_analizada": "Interior framing",
  "fecha_generacion": "2026-02-26T12:39:24.632Z",
  "input_snapshot": { ... },
  "output_analisis": {
    "general_project_status": "Texto descriptivo...",
    "execution_schedule_analysis": "Texto descriptivo...",
    "safety_compliance_analysis": "Texto descriptivo...",
    "technical_approvals_analysis": "Texto descriptivo...",
    "overall_observation": "Observación mayor a 50 caracteres...",
    "risk_level": "medium",
    "detected_inconsistencies": []
  },
  "modelo_utilizado": "arcee-ai/trinity-large-preview:free",
  "prompt_version_id": 1
}

**Manejo de Errores Esperados:**
* **`422 Unprocessable Entity`:** Ocurre si la IA "alucina" y devuelve un formato inválido, omite claves requeridas o no cumple con las restricciones de longitud (ej. `overall_observation` < 50 caracteres). El backend rechaza la respuesta para proteger la integridad de la base de datos.
* **`502 Bad Gateway`:** Ocurre por errores de comunicación externos (OpenRouter caído, Timeout superado, API Key sin saldo o Rate Limit excedido).
* **`500 Internal Server Error`:** Error crítico interno del servidor (ej. fallo al guardar en PostgreSQL).

---

## 2. Logs y Métricas de IA

Este módulo expone la tabla `log_peticiones`, la cual es alimentada internamente cada vez que se procesa un reporte.

### `GET /logs/`
**Descripción:** Devuelve un historial paginado con las métricas de uso y rendimiento de la IA para auditar costos y tiempos de respuesta.

**Query Parameters:**
* `limite` (integer, default: 50): Cantidad máxima de registros a devolver. Previene la saturación de memoria.

**Respuesta Exitosa (200 OK):**
Retorna un array de objetos con detalles de consumo (`tokens_entrada`, `tokens_salida`), el costo calculado (`costo_estimado`), la latencia (`tiempo_ejecucion_ms`) y el código de estado HTTP (`status_code`).

[
  {
    "id": 2,
    "reporte_id": "f34ef4ca-ea94-457c-9f68-907980c30e1e",
    "tokens_entrada": 502,
    "tokens_salida": 198,
    "costo_estimado": 0.0898,
    "tiempo_ejecucion_ms": 7056,
    "status_code": 200,
    "fecha_evento": "2026-02-26T12:39:24.696Z"
  }
]

---

### `GET /logs/{reporte_id}`
**Descripción:** Permite realizar una búsqueda quirúrgica para obtener las métricas exactas de consumo generadas por un reporte de análisis en particular.

**Path Parameters:**
* `reporte_id` (UUID, Requerido): El identificador único del reporte (`reporte_id`) generado previamente en `/reportes/`.

**Respuesta Exitosa (200 OK):**

{
  "id": 2,
  "reporte_id": "f34ef4ca-ea94-457c-9f68-907980c30e1e",
  "tokens_entrada": 502,
  "tokens_salida": 198,
  "costo_estimado": 0.0898,
  "tiempo_ejecucion_ms": 7056,
  "status_code": 200,
  "fecha_evento": "2026-02-26T12:39:24.696Z"
}

**Manejo de Errores Esperados:**
* **`404 Not Found`:** Se devuelve si el UUID proporcionado no existe en la tabla de logs.
* **`422 Unprocessable Entity`:** Se lanza automáticamente por FastAPI si el parámetro pasado en la URL no respeta el formato estándar de un UUID.