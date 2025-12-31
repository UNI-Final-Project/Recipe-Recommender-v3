# 📊 FLUJO COMPLETO DEL SISTEMA - Recipe Recommender con MLOps

## 🎯 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENTE / USUARIO                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    HTTP REST API
                           │
        ┌──────────────────▼──────────────────┐
        │                                      │
        │    🚀 FASTAPI UVICORN SERVER        │
        │      (Puerto 8000)                  │
        │                                      │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼──────┐    ┌──────▼────┐
   │ Modelos │      │   Datos    │    │  MLOps    │
   │ ML      │      │  53K recetas│    │  System   │
   └────┬────┘      └─────┬──────┘    └──────┬────┘
        │                  │                   │
   ┌────▼────────┐  ┌─────▼──────┐  ┌────────▼────────┐
   │MLflow       │  │ Qdrant     │  │7 Módulos MLOps  │
   │Tracking     │  │ Vector DB  │  │- Registry       │
   │Experiments  │  │ Embeddings │  │- Evaluation     │
   └─────────────┘  └────────────┘  │- Monitoring     │
                                     │- Retraining    │
                                     │- Logging       │
                                     └────────────────┘
```

---

## 🔄 Flujo Completo de Uso

### PASO 1: Iniciar el Servidor
```bash
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"
& "venv\Scripts\python.exe" -m uvicorn app:app --port 8000
```

**Logs Esperados:**
```
2025-12-31 00:19:16,003 - mlops.model_registry - INFO - Registry loaded with 1 models
2025-12-31 00:19:17,849 - app - INFO - Data loaded: 53064 recipes
2025-12-31 00:19:18,057 - app - INFO - MLflow tracking enabled: ./mlruns
2025-12-31 00:19:18,057 - mlops - INFO - MLOps system initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

### PASO 2: Acceder a Documentación Interactiva

**Swagger UI (Recomendado):**
```
http://127.0.0.1:8000/docs
```

**ReDoc:**
```
http://127.0.0.1:8000/redoc
```

---

## 🔌 Endpoints Disponibles

### 1. GET `/` - Información de la API
**Propósito:** Obtener información general del servidor

**Respuesta:**
```json
{
  "message": "Recipe Recommender API - MLOps Edition",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "redoc": "/redoc",
    "recommend": "/recommend",
    "metrics": "/metrics",
    "models": "/models"
  }
}
```

---

### 2. GET `/health` - Verificar Salud del Sistema
**Propósito:** Monitoreo de la aplicación

**Respuesta Esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-31T00:19:18.057000",
  "service": "Recipe Recommender API",
  "version": "1.0.0",
  "data_loaded": true,
  "num_recipes": 53064,
  "model_production": "hybrid_ranker v1.0.0"
}
```

---

### 3. POST `/recommend` - Obtener Recomendaciones
**Propósito:** Generar recomendaciones de recetas basadas en una consulta

**Request:**
```json
{
  "query": "delicious pasta with tomato and garlic"
}
```

**Respuesta Esperada:**
```json
{
  "recetas": [
    {
      "nombre": "Classic Spaghetti al Pomodoro",
      "descripción": "Traditional Italian pasta with fresh tomato sauce",
      "ingredientes": ["spaghetti", "tomatoes", "garlic", "olive oil", "basil"],
      "instrucciones": ["Cook pasta", "Prepare sauce", "Combine"],
      "calificación_promedio": 4.8
    },
    {
      "nombre": "Garlic Pasta with Herbs",
      "descripción": "Simple but flavorful garlic pasta dish",
      "ingredientes": ["pasta", "garlic", "herbs", "oil"],
      "instrucciones": ["Cook pasta", "Sauté garlic"],
      "calificación_promedio": 4.5
    },
    {
      "nombre": "Creamy Tomato Pasta",
      "descripción": "Rich and creamy pasta with tomato",
      "ingredientes": ["pasta", "tomato", "cream", "garlic"],
      "instrucciones": ["Cook pasta", "Make sauce"],
      "calificación_promedio": 4.6
    }
  ]
}
```

**Proceso Interno:**
1. 🔍 Genera embedding de la consulta con OpenAI (text-embedding-3-small)
2. 🔎 Busca en Qdrant Vector DB (5000 vectores)
3. 🎯 Realiza ranking híbrido (semantic + popularity)
4. 📊 Recolecta métricas
5. 📝 Registra en MLflow
6. ⚡ Traduce respuesta al español

---

### 4. GET `/metrics` - Métricas del Sistema
**Propósito:** Obtener métricas de rendimiento

**Respuesta Esperada:**
```json
{
  "total_requests": 42,
  "avg_latency_ms": 245.5,
  "error_rate": 0.0,
  "requests_by_endpoint": {
    "/recommend": 25,
    "/health": 10,
    "/models": 7
  },
  "performance_metrics": {
    "p50_latency": 200,
    "p95_latency": 400,
    "p99_latency": 800
  }
}
```

---

### 5. GET `/models` - Lista de Modelos
**Propósito:** Obtener todos los modelos registrados

**Respuesta Esperada:**
```json
{
  "models": [
    {
      "model_id": "hybrid_ranker",
      "version": "1.0.0",
      "status": "production",
      "model_type": "hybrid",
      "created_at": "2025-12-31T00:19:18",
      "metrics": {
        "alpha": 0.7,
        "status": "production"
      }
    }
  ]
}
```

---

### 6. GET `/models/{model_id}/production` - Detalles del Modelo
**Propósito:** Obtener detalles del modelo en producción

**URL:**
```
GET /models/hybrid_ranker/production
```

**Respuesta Esperada:**
```json
{
  "model_id": "hybrid_ranker",
  "model_type": "hybrid",
  "version": "1.0.0",
  "status": "production",
  "description": "Hybrid semantic + popularity ranker",
  "created_at": "2025-12-31T00:19:18",
  "parameters": {
    "embedding_model": "text-embedding-3-small",
    "llm_model": "gpt-4-1106-preview",
    "ranking_algorithm": "hybrid",
    "features": ["semantic_score", "popularity_score"]
  },
  "metrics": {
    "alpha": 0.7,
    "status": "production"
  },
  "tags": {
    "environment": "production",
    "initial_version": "true"
  }
}
```

---

### 7. POST `/retrain/check` - Verificar Retraining
**Propósito:** Verificar si hay modelos que necesiten retraining

**Respuesta Esperada:**
```json
{
  "needs_retraining": false,
  "models_checked": ["hybrid_ranker"],
  "details": {
    "hybrid_ranker": {
      "days_since_training": 0,
      "performance_degradation": 0.0,
      "data_drift_detected": false,
      "recommendation": "No retraining needed"
    }
  }
}
```

---

## 📊 Sistema MLOps en Acción

### Componentes Activos:

#### 1. **Model Registry** 🏛️
- Almacena y versionea modelos
- Tracking de metadatos
- Gestión de estados (staging, production)

#### 2. **Evaluation Module** 📈
- Calcula métricas del modelo:
  - Accuracy, Precision, Recall
  - MRR (Mean Reciprocal Rank)
  - NDCG (Normalized Discounted Cumulative Gain)
- Detecta data drift
- Genera reportes automáticos

#### 3. **Monitoring System** 👁️
- Recolecta métricas en tiempo real
- Detecta anomalías
- Health checks automáticos
- Alertas de degradación

#### 4. **Logging** 📝
- Logs estructurados en JSON
- Múltiples loggers:
  - `app_logger` - Aplicación
  - `mlops_logger` - MLOps
  - `monitoring_logger` - Monitoreo

#### 5. **Retraining Orchestrator** 🔄
- Verifica necesidad de retraining
- Ejecuta jobs automáticos
- Compara modelos
- Promociona a producción

#### 6. **MLflow Tracking** 📊
- Experimenta registro:
  - Parámetros
  - Métricas
  - Modelos
  - Artifacts
- Interfaz web en `http://127.0.0.1:5000`

---

## 🎬 Secuencia de Eventos Típica

```
1. Usuario envía consulta
           │
           ▼
2. Endpoint /recommend recibe petición
           │
           ▼
3. Genera embedding con OpenAI
           │
           ▼
4. Busca en Qdrant Vector DB
           │
           ▼
5. Aplica ranking híbrido
           │
           ▼
6. Recolecta métricas
           │
           ▼
7. Registra en MLflow
           │
           ▼
8. Traduce respuesta
           │
           ▼
9. Retorna recomendaciones
           │
           ▼
10. Logger registra evento
```

---

## 🔧 Configuración de Entorno

**Variables Necesarias (en `.env`):**
```env
OPENAI_API_KEY=sk-...
QDRANT_API_KEY=...
QDRANT_HOST=https://...
MLFLOW_TRACKING_URI=./mlruns
MLFLOW_EXPERIMENT_NAME=recipe-recommendations
DATA_PKL=food.pkl
```

---

## 📁 Estructura de Archivos MLOps

```
mlops/
├── __init__.py              # Exporta todo
├── config.py                # Configuración centralizada
├── logging_config.py        # 5 loggers estructurados
├── model_registry.py        # Versionado de modelos
├── evaluation.py            # 15+ métricas
├── monitoring.py            # Recolección en tiempo real
└── retraining.py           # Orquestación automática
```

---

## 🚀 Próximos Pasos Recomendados

1. **Acceder a Swagger UI:**
   ```
   http://127.0.0.1:8000/docs
   ```
   - Prueba cada endpoint interactivamente
   - Visualiza esquemas de request/response

2. **Ver MLflow UI:**
   ```bash
   mlflow ui --backend-store-uri ./mlruns
   ```
   - Accede a `http://127.0.0.1:5000`
   - Monitorea experimentos

3. **Revisar Logs:**
   ```bash
   ls -la logs/
   ```
   - Archivos JSON con todos los eventos

4. **Verificar Métricas:**
   - GET `/metrics` periodicamente
   - Identifica tendencias

5. **Probar Retraining:**
   - POST `/retrain/check`
   - Verifica necesidad de actualización

---

## ✅ Verificación Final

Cuando el servidor esté corriendo correctamente, deberías ver:

```
✓ 53,064 recetas cargadas
✓ 1 modelo en producción
✓ MLflow tracking activado
✓ 7 módulos MLOps activos
✓ Logs en tiempo real
✓ Métricas siendo recolectadas
✓ API respondiendo en puerto 8000
```

**Fecha:** 31 de Diciembre de 2025
**Estado:** ✅ SISTEMA OPERATIVO COMPLETO
