# Documentación de la API  - Reno USA AI Backend

Esta documentación detalla los endpoints disponibles para la generación de reportes de obra impulsados por Inteligencia Artificial y el monitoreo de su rendimiento.

**Base URL:** `http://localhost:8000/api/v1`

---

## 1. Reportes Generados

### `POST /reportes/`
**Descripción:** Recibe un snapshot con el estado actual de una obra, lo envía al motor de IA (OpenRouter) para su evaluación técnica, y guarda el resultado junto con el contexto en la tabla `reportes_generados`.

**Request Body (JSON):**
Espera un objeto que contenga el `snapshot` detallado de la obra.

```json
{
  "snapshot": {
    "project_code": "RENO-US-2026-009",
    "project_name": "Residential Remodeling – Montecito",
    "location": "Montecito, California",
    "current_phase": "Interior framing",
    "phase_completion_percentage": 60,
    "schedule_deviation_days": 1,
    "tasks_performed": ["Drywall installation", "Electrical rough-in"],
    "trades_on_site": ["Framing crew", "Electrical contractor"],
    "safety_measures": ["Hard hats enforced", "PPE mandatory"],
    "worker_coverage": {
      "status": "Active",
      "coverage_type": "Workers' Compensation",
      "policy_reference": "WC-CA-882134"
    },
    "technical_approval": {
      "approval_date": "2026-04-22",
      "approval_status": "Approved",
      "licensed_professional": "Michael Anderson, Architect"
    },
    "supervisor_notes": "Minor delay due to material delivery",
    "incidents_reported": 0
  }
}
```
**Respuesta Exitosa (200 OK):**
```json
{
  "id": "302bf0d6-2eb0-4b9f-bf57-1e9f9c1fab84",
  "analisis": {
    "general_project_status": "The project is progressing well...",
    "execution_schedule_analysis": "One day delay detected...",
    "safety_compliance_analysis": "Safety measures are strictly followed...",
    "technical_approvals_analysis": "Licensed professional approval obtained...",
    "overall_observation": "The overall advancement is positive despite minor material logistics...",
    "risk_level": "low",
    "detected_inconsistencies": []
  }
}
```

**Manejo de Errores Esperados:**
* **`422 Unprocessable Entity`:** Ocurre si la IA "alucina" y devuelve un formato inválido, omite claves requeridas o no cumple con las restricciones de longitud (ej. `overall_observation` < 50 caracteres). El backend rechaza la respuesta para proteger la integridad de la base de datos.
* **`502 Bad Gateway`:** Ocurre por errores de comunicación externos (OpenRouter caído, Timeout superado, API Key sin saldo o Rate Limit excedido).
* **`500 Internal Server Error`:** Error crítico interno del servidor (ej. fallo al guardar en PostgreSQL).

### `GET /reportes/{reporte_id}`
**Descripción:** Obtiene el detalle completo de un reporte histórico mediante su UUID. Incluye el snapshot original de entrada y metadatos de la IA.

---

## 2. Logs y Métricas de IA

Este módulo expone la tabla `log_peticiones`, la cual es alimentada internamente cada vez que se procesa un reporte.

### `GET /logs/`
**Descripción:** Devuelve un historial paginado con las métricas de uso y rendimiento de la IA para auditar costos y tiempos de respuesta.

**Query Parameters:**
* `limite` (integer, default: 50): Cantidad máxima de registros a devolver. Previene la saturación de memoria.

**Respuesta Exitosa (200 OK):**
Retorna un array de objetos con detalles de consumo (`tokens_entrada`, `tokens_salida`), el costo calculado (`costo_estimado`), la latencia (`tiempo_ejecucion_ms`) y el código de estado HTTP (`status_code`).
```json
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
```
---

### `GET /logs/{reporte_id}`
**Descripción:** Permite realizar una búsqueda para obtener las métricas exactas de consumo generadas por un reporte de análisis en particular.

**Path Parameters:**
* `reporte_id` (UUID, Requerido): El identificador único del reporte (`reporte_id`) generado previamente en `/reportes/`.

**Respuesta Exitosa (200 OK):**
```json
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
```
**Manejo de Errores Esperados:**
* **`404 Not Found`:** Se devuelve si el UUID proporcionado no existe en la tabla de logs.
* **`422 Unprocessable Entity`:** Se lanza automáticamente por FastAPI si el parámetro pasado en la URL no respeta el formato estándar de un UUID.


---

## 3. Gestión de Prompt Templates
Permite administrar dinámicamente las instrucciones de la IA. Solo puede haber un prompt activo en el sistema a la vez.

### `POST /prompts/`

**Descripción**: Crea una nueva plantilla de prompt en el sistema.
```json
{
  "nombre_codigo": "auditor_base",
  "version": 1,
  "template_text": "You are an expert construction project auditor for Reno USA...",
  "activo": true
}
```
**Aclaración:** el prompt cargado en el swagger por defecto contiene el `template_text` para generar la respuesta válida correspondiente con el formato preestablecido. Ya que si la respueta no cumple con el formato, ésta será rechazada.

### `GET /prompts/`

**Descripción**: Lista todos los prompts registrados con soporte para paginación `(skip, limit)` y filtrado `(activo_only)`.

```json
[
  {
    "nombre_codigo": "auditor_base",
    "version": 2,
    "template_text": "You are an expert construction project  auditor for Reno USA...",
    "activo": false
  }
]
```

### `GET /prompts/{prompt_id}`

**Descripción**: Devuelve un prompt en específico según id.

### `GET /prompts/active`

**Descripción**: Devuelve la plantilla de prompt que está controlando actualmente el servicio de IA.

### `PUT /prompts/{prompt_id}`

**Descripción**: Actualiza el texto o estado de un prompt. El id, version y nombre_codigo no son modificables.
```json
{
  "template_text": "Texto corregido para el prompt...",
  "activo": true
}
```

### `DELETE /prompts/{prompt_id}`

**Descripción**: Eliminación permanente del registro. No se permite borrar el prompt marcado como `activo`.

### `PATCH /prompts/{prompt_id}/activate`

**Descripción**: Activa el prompt indicado y desactiva automáticamente todos los demás para mantener la consistencia.

### `PATCH /prompts/{prompt_id}/deactivate`

**Descripción**: Desactiva un prompt específico.

