# Flujo de Ejecución: Generación de Reportes con IA

Este documento describe el ciclo de vida completo de una petición dentro del Microservicio de IA (Reno USA). Este microservicio opera de forma aislada y **únicamente se comunica con el Backend Principal**, sin tener interacción directa con el Frontend del usuario.

## Arquitectura de Tablas Involucradas
El flujo interactúa secuencialmente con tres tablas de nuestra base de datos PostgreSQL:
1.  **`prompts_templates`**: Almacena las instrucciones de comportamiento (templates) para la IA, su versión y estado activo.
2.  **`reportes_generados`**: Almacena la trazabilidad de la obra, guardando el snapshot de entrada y el análisis resultante de la IA.
3.  **`log_peticiones`**: Registra las métricas exactas de rendimiento (tiempo, costo, tokens) de cada llamada a la API externa.

---

## Paso a Paso del Flujo

### Paso 1: Recepción y Validación Inicial
1. El **Backend Principal** envía una petición `POST /api/v1/reportes/` hacia nuestro microservicio.
2. El *Payload* (cuerpo de la petición) incluye el `snapshot` con los datos de la obra y un identificador del prompt (ej: `nombre_codigo` = "auditor_base").
3. **Escudo Pydantic:** FastAPI valida automáticamente que el JSON entrante tenga la estructura esperada. Si el Backend Principal mandó algo mal formado, se devuelve un Error `422 Unprocessable Entity` inmediatamente, protegiendo nuestra base de datos.

### Paso 2: Obtención del Prompt (Base de Datos)
1. El sistema consulta la tabla `prompts_templates` buscando el registro que coincida con el `nombre_codigo` recibido y que tenga el campo `activo` en `True`.
2. Se extrae el `template_text` (las instrucciones base para la IA) y su `id` (para la trazabilidad de la versión usada).

### Paso 3: Preparación y Llamada a la IA (OpenRouter)
1. El servicio de IA (`ai_service.py`) inyecta el `snapshot` recibido dentro del `template_text`.
2. Se inicia un **cronómetro interno** para medir la latencia de la red y del modelo.
3. Se realiza una petición HTTP asíncrona a la API externa de OpenRouter.

### Paso 4: Recepción, Limpieza y Validación Estricta
1. OpenRouter devuelve la respuesta. [cite_start]Se detiene el cronómetro y se calcula el `tiempo_ejecucion_ms`.
2. Se extraen los metadatos de consumo: `tokens_entrada`, `tokens_salida` y el `modelo_utilizado` real.
3. El texto de la respuesta se "limpia" de posibles formatos Markdown (ej: ````json ... ````).
4. **Fail Fast (Validación de Salida):** El texto limpio se pasa por un validador estricto de Pydantic. Se verifica que sea un JSON válido y que contenga todos los campos obligatorios del análisis.
   * *Si la IA falló o alucinó:* Se aborta la operación y se lanza un Error `422` hacia el Backend Principal. No se guarda el reporte roto.

### Paso 5: Persistencia del Reporte
1. Con el análisis validado, se crea un nuevo registro en la tabla `reportes_generados`.
2. Se genera un `id` único (UUID).
3. Se guarda el JSON original en `input_snapshot`, el JSON de la IA en `output_analisis`, y se asocia la petición con el `prompt_version_id`.

### Paso 6: Registro de Métricas y Auditoría
1. [cite_start]Inmediatamente después, se crea un registro en la tabla `log_peticiones`.
2. [cite_start]Se vincula este log al reporte recién creado mediante el `reporte_id`.
3. [cite_start]Se guardan las métricas: `tiempo_ejecucion_ms`, `tokens_entrada`, `tokens_salida`, `status_code` y se calcula el `costo_estimado`.

### Paso 7: Respuesta al Backend Principal
1. El flujo interno finaliza exitosamente.
2. Nuestro Microservicio le devuelve al **Backend Principal** un código `200 OK` con el `id` del reporte generado y el análisis de la IA.
3. El Backend Principal recibe esta información y se encarga, por su cuenta, de procesarla o reenviarla al Frontend del cliente final.