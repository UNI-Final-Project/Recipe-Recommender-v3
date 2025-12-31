# 🍳 Recipe Recommender v3 - MLOps Enabled

Un sistema de recomendación de recetas basado en inteligencia artificial con **capacidades completas de MLOps**.

## 🌟 Características Principales

- 🤖 **Recomendaciones Inteligentes** - Búsqueda semántica con embeddings de OpenAI
- 🏪 **Almacenamiento Vectorial** - Integración con Qdrant Cloud
- 🌐 **Traducción Multiidioma** - Soporte para múltiples idiomas con GPT-4
- 🎯 **Ranking Híbrido** - Combinación de relevancia semántica y popularidad
- 
### 🚀 MLOps Features

- ✅ **Versionado de Modelos** - Semantic versioning con estado completo (training/validation/production/archived)
- ✅ **Evaluación de Modelos** - Métricas de ranking, clasificación y recuperación
- ✅ **Monitoreo en Tiempo Real** - Tracking de latencia, errores y anomalías
- ✅ **Logging Estructurado** - Logs centralizados en formato JSON
- ✅ **Retraining Automático** - Pipeline programable de reentrenamiento
- ✅ **Detección de Anomalías** - Z-score y detección de degradación
- ✅ **Data Validation** - Validación de datos y detección de drift
- ✅ **MLflow Integration** - Tracking completo de experimentos

## 📁 Estructura del Proyecto

```
Recipe-Recommender-v3/
├── app.py                          # API FastAPI con MLOps integrado
├── schedule_retraining.py          # Script de retraining automático
├── test_mlops.py                   # Tests y ejemplos
│
├── mlops/                          # Módulo de MLOps
│   ├── __init__.py                # Inicialización del módulo
│   ├── config.py                  # Configuración centralizada
│   ├── logging_config.py           # Sistema de logging
│   ├── model_registry.py           # Versionado de modelos
│   ├── evaluation.py               # Evaluación y métricas
│   ├── monitoring.py               # Monitoreo en tiempo real
│   ├── retraining.py               # Pipeline de retraining
│   └── data_schema.json            # Schema de datos
│
├── logs/                           # Archivos de log (JSON)
├── models/                         # Registry de modelos
│   └── registry.json               # Metadatos de modelos
├── mlruns/                         # MLflow tracking
│
├── MLOPS_GUIDE.md                  # Guía completa de MLOps
├── requirements.txt                # Dependencias
└── README.md                       # Este archivo
```

## 🚀 Quick Start

### Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd Recipe-Recommender-v3

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cp .env.example .env
# Editar .env con tus credenciales
```

### Configurar Variables de Entorno

```bash
# .env
OPENAI_API_KEY=sk-...
QDRANT_API_KEY=your_key
QDRANT_HOST=https://...

# MLOps
MLFLOW_TRACKING_URI=./mlruns
MLFLOW_EXPERIMENT_NAME=recipe-recommendations
MONITORING_ENABLED=true
RETRAIN_ENABLED=true
```

### Ejecutar la API

```bash
# Desarrollo con hot reload
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Producción
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Ver MLflow UI

```bash
mlflow ui --backend-store-uri ./mlruns
# Abre: http://localhost:5000
```

## 📊 API Endpoints

### Recomendaciones

```bash
POST /recommend
{
  "query": "recetas con pollo"
}
```

### Salud del Sistema

```bash
GET /health
```

### Métricas en Tiempo Real

```bash
GET /metrics?window_minutes=60
```

### Modelos Registrados

```bash
GET /models
GET /models/{model_id}/production
```

### Verificar Retraining

```bash
POST /retrain/check
```

## 🔧 Uso de MLOps

### Registrar un Modelo

```python
from mlops import model_registry, ModelMetadata

metadata = ModelMetadata(
    model_id="hybrid_ranker",
    model_type="hybrid",
    version="1.0.1",
    description="Improved ranking model",
    metrics={"accuracy": 0.92, "f1": 0.89},
    status="validation"
)

model_registry.register_model(metadata)
```

### Evaluar Modelo

```python
from mlops import ModelEvaluator
import numpy as np

evaluator = ModelEvaluator()
y_true = np.array([4, 3, 5, 2, 1])
y_pred = np.array([3.8, 3.2, 5.1, 2.3, 1.1])

metrics = evaluator.calculate_ranking_metrics(y_true, y_pred)
```

### Monitoreo

```python
from mlops import metrics_collector, anomaly_detector

# Registrar métrica
metrics_collector.record("api_latency_ms", 145.5)

# Detectar anomalías
values = np.array([10, 12, 11, 13, 100, 12])
result = anomaly_detector.detect_anomalies(values, threshold=3.0)
```

### Retraining Automático

```python
from mlops import auto_scheduler

# Verificar y programar retraining
results = auto_scheduler.check_and_schedule_retraining(["hybrid_ranker"])
```

## 📚 Documentación Completa

Ver [MLOPS_GUIDE.md](MLOPS_GUIDE.md) para:

- Arquitectura completa de MLOps
- Guía de uso de cada módulo
- Ejemplos de código
- API reference
- Troubleshooting

## 🧪 Tests

```bash
# Ejecutar todos los tests
python test_mlops.py

# Ejecutar con unittest
python -m unittest test_mlops.TestModelRegistry -v
```

## 📈 Monitoreo en Producción

### Dashboard MLflow

```bash
mlflow ui --backend-store-uri ./mlruns --host 0.0.0.0 --port 5000
```

### Ver Logs Estructurados

```bash
# Seguir logs en tiempo real
tail -f logs/app_*.log | jq '.'

# Filtrar por nivel
grep "ERROR" logs/mlops_*.log
```

### Alertas

El sistema genera alertas cuando:
- Latencia > 5000ms
- Tasa de error > 5%
- Accuracy degrada > 5%
- Anomalías detectadas (z-score > 3)

## 🐳 Docker

```bash
# Build
docker build -t recipe-recommender .

# Run
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e QDRANT_API_KEY=... \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/mlruns:/app/mlruns \
  recipe-recommender
```

## 🔄 Retraining Automático

```bash
# Ejecutar verificación de retraining
python schedule_retraining.py

# Con APScheduler (producción)
python schedule_retraining.py  # seleccionar opción 3
```

## 📊 Métricas Recopiladas

- `api_latency_ms` - Latencia de API
- `translation_latency_ms` - Latencia de traducción
- `embedding_latency_ms` - Latencia de embeddings
- `num_recipes` - Recetas retornadas
- `request_count` - Total de solicitudes
- `error_rate` - Tasa de error (%)

Métricas de modelo:
- Ranking: MSE, MAE, RMSE, R², NDCG, MRR
- Clasificación: Accuracy, Precision, Recall, F1

## 🐛 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'mlops'`

```bash
# Asegurar que estás en el directorio correcto
cd /path/to/Recipe-Recommender-v3
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Error: Permisos en logs

```bash
chmod 755 logs/ mlops/
```

### MLflow no se conecta

```bash
# Verificar URI
mlflow ui --backend-store-uri ./mlruns

# Ajustar .env
MLFLOW_TRACKING_URI=http://localhost:5000
```

## 📝 Logging

Logs disponibles en `logs/`:
- `app_*.log` - Logs de aplicación
- `mlops_*.log` - Logs de MLOps
- `monitoring_*.log` - Logs de monitoreo
- `model_training_*.log` - Logs de entrenamiento
- `retraining_*.log` - Logs de retraining

Formato: JSON estructurado con contexto completo

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature
3. Implementa cambios con MLOps
4. Agrega tests
5. Push y crea Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT.

## 👥 Autor

Desarrollado por el equipo de Data Science

---

**Última actualización:** 30 de diciembre, 2024
