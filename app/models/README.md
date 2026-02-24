# 📁 MODELS - Estructura Organizada

## 📊 Estructura de Archivos

```
app/models/
├── __init__.py              # Exporta todos los schemas
├── enums.py                 # Enumeraciones compartidas (RiskLevel, StatusCode)
├── common.py                # Schemas comunes (HealthCheck, Error, Paginación)
├── prompt_template.py       # Schemas de prompts templates (tabla prompts_templates)
├── project_snapshot.py      # Schema del input del backend (campo JSONB)
├── analysis_output.py       # Schema del output de la IA (campo JSONB)
├── reporte_generado.py      # Schemas de reportes + API Request/Response
└── log_peticion.py          # Schemas de logs (tabla log_peticiones)
```

---

## 🎯 Mapeo: Tabla DB → Archivo Python

| Tabla en PostgreSQL | Archivo Python | Schemas principales |
|---------------------|----------------|---------------------|
| `prompts_templates` | `prompt_template.py` | PromptTemplateCreate, PromptTemplateResponse |
| `reportes_generados` | `reporte_generado.py` | ReporteGeneradoCreate, ReporteGeneradoResponse |
| `log_peticiones` | `log_peticion.py` | LogPeticionCreate, LogPeticionResponse |
| N/A (común) | `common.py` | ErrorResponse, HealthCheckResponse |
| N/A (enums) | `enums.py` | RiskLevel, StatusCode |

---

## 📝 Detalle de cada archivo

### **enums.py**
**Propósito:** Enumeraciones compartidas en todo el sistema
- `RiskLevel`: Niveles de riesgo (low, medium, high)
- `StatusCode`: Códigos HTTP para logs

---

### **prompt_template.py**
**Propósito:** Todo relacionado con la tabla `prompts_templates`

**Schemas de DB:**
- `PromptTemplateBase`: Schema base
- `PromptTemplateCreate`: Para crear prompts
- `PromptTemplateUpdate`: Para actualizar prompts
- `PromptTemplateResponse`: Respuesta completa
- `PromptTemplateListItem`: Resumen para listados
- `ActivePromptResponse`: Prompt activo actual

---

### **project_snapshot.py**
**Propósito:** Estructura del snapshot que recibe del backend

**Schema principal:**
- `ProjectSnapshot`: Define la estructura del campo `input_snapshot` (JSONB) en `reportes_generados`

**Contiene:**
- Datos del proyecto (code, name, location)
- Período analizado
- Estado de la fase
- Tareas ejecutadas
- Trades en sitio
- Medidas de seguridad
- Cobertura de trabajadores
- Aprobaciones técnicas

---

### **analysis_output.py**
**Propósito:** Estructura del análisis generado por la IA

**Schema principal:**
- `AnalysisOutput`: Define la estructura del campo `output_analisis` (JSONB) en `reportes_generados`

**Contiene:**
- General project status
- Execution schedule analysis
- Safety compliance analysis
- Technical approvals analysis
- Overall observation
- Risk level
- Detected inconsistencies

---

### **reporte_generado.py**
**Propósito:** Todo relacionado con la tabla `reportes_generados` + Schemas de API

**Schemas de DB:**
- `ReporteGeneradoCreate`: Para crear reportes
- `ReporteGeneradoResponse`: Respuesta completa desde DB
- `ReporteGeneradoListItem`: Resumen para listados
- `ReporteGeneradoDetailResponse`: Detalle completo

**Schemas de API:**
- `GenerateAnalysisRequest`: Request del endpoint principal
- `GenerateAnalysisResponse`: Response después de generar análisis

---

### **log_peticion.py**
**Propósito:** Todo relacionado con la tabla `log_peticiones`

**Schemas de DB:**
- `LogPeticionCreate`: Para crear logs
- `LogPeticionResponse`: Respuesta desde DB
- `LogPeticionSummary`: Estadísticas de logs
- `LogPeticionDetailResponse`: Detalle con metadata calculada
- `LogPeticionFilters`: Filtros para consultar logs

---

## 🔗 Cómo usar los schemas

### **Importación simple:**
```python
from app.models import (
    GenerateAnalysisRequest,
    AnalysisOutput,
    PromptTemplateResponse,
    RiskLevel
)
```

### **Importación por módulo:**
```python
from app.models.reporte_generado import GenerateAnalysisRequest
from app.models.prompt_template import PromptTemplateCreate
```

---

## ✅ Ventajas de esta estructura

1. **Separación de responsabilidades** - Cada archivo tiene UN propósito claro
2. **Fácil navegación** - Sabés exactamente dónde buscar
3. **Escalable** - Agregar nuevos schemas no rompe nada
4. **Mantenible** - Cambios aislados por archivo
5. **Testing friendly** - Podés testear cada módulo por separado
6. **Git friendly** - Menos conflictos en merges

---


## 🎯 Siguiente paso

Una vez que tengas los models, el siguiente paso es crear:
- **Database models (SQLAlchemy)** - Las tablas en código
- **Services** - Lógica de negocio
- **Endpoints** - API REST

---

**¡Los schemas están listos y organizados profesionalmente!** 🚀
