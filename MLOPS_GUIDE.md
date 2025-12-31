# MLOps Implementation Guide - Recipe Recommender

## 📋 Visión General

Este proyecto implementa un sistema completo de **MLOps** (Machine Learning Operations) que incluye:

1. **Versionado de Modelos** - Tracking y registro de versiones de modelos
2. **Evaluación y Validación** - Métricas de rendimiento y validación de datos
3. **Monitoreo** - Monitoreo en tiempo real de latencia, errores y anomalías
4. **Logging Estructurado** - Logs centralizados en formato JSON
5. **Retraining Automático** - Pipeline para reentrenamiento de modelos

---

## 🏗️ Arquitectura de Directorios

```
Recipe-Recommender-v3/
├── app.py                          # API principal mejorada
├── mlops/                          # Módulo de MLOps
│   ├── __init__.py                # Inicialización del módulo
│   ├── config.py                  # Configuración centralizada
│   ├── logging_config.py           # Sistema de logging estructurado
│   ├── model_registry.py           # Registro y versionado de modelos
│   ├── evaluation.py               # Evaluación y métricas
│   ├── monitoring.py               # Monitoreo en tiempo real
│   └── retraining.py               # Pipeline de retraining
├── logs/                           # Archivos de log
├── mlruns/                         # Tracking de MLflow
├── models/                         # Modelos entrenados
│   └── registry.json               # Registro de modelos (JSON)
└── requirements.txt                # Dependencias
```

---

## 🔧 Configuración

### Variables de Entorno (.env)

```bash
# MLflow
MLFLOW_TRACKING_URI=./mlruns
MLFLOW_EXPERIMENT_NAME=recipe-recommendations

# Monitoreo
MONITORING_ENABLED=true
ALERT_THRESHOLD_LATENCY=5000          # ms
ALERT_THRESHOLD_ACCURACY_DROP=0.05    # 5%

# Retraining
RETRAIN_ENABLED=true
RETRAIN_INTERVAL_DAYS=7
RETRAIN_DATA_THRESHOLD=100

# Logging
LOG_LEVEL=INFO
MAX_LOG_SIZE_MB=50
BACKUP_COUNT=5
```

---

## 📊 Módulos Principales

### 1. Model Registry (Versionado de Modelos)

Gestiona el ciclo de vida completo de los modelos.

#### Uso:

```python
from mlops import model_registry, ModelMetadata

# Registrar un nuevo modelo
metadata = ModelMetadata(
    model_id="hybrid_ranker",
    model_type="hybrid",
    version="1.0.1",
    description="Improved hybrid ranker",
    metrics={
        "accuracy": 0.92,
        "precision": 0.89,
        "recall": 0.85,
        "f1_score": 0.87
    },
    parameters={
        "embedding_model": "text-embedding-3-small",
        "alpha": 0.7
    },
    status="validation",
    tags={"author": "data_team", "environment": "staging"}
)

model_registry.register_model(metadata)

# Obtener modelo en producción
prod_model = model_registry.get_production_model("hybrid_ranker")

# Listar modelos
models = model_registry.list_models(status="production")

# Promover a producción
model_registry.update_model_status("hybrid_ranker", "1.0.1", "production")

# Ver historial de versiones
history = model_registry.get_version_history("hybrid_ranker")
```

#### Características:

- ✅ Semantic versioning (major.minor.patch)
- ✅ Estados: training → validation → production → archived
- ✅ Persistencia en JSON
- ✅ Integración con MLflow

---

### 2. Evaluation Module (Evaluación y Métricas)

Calcula métricas de rendimiento y detecta data drift.

#### Uso:

```python
from mlops import ModelEvaluator, ModelValidator, EvaluationReport
import numpy as np

evaluator = ModelEvaluator()
validator = ModelValidator()

# Calcular métricas de ranking
y_true = np.array([4, 3, 5, 2, 1])
y_pred = np.array([3.8, 3.2, 5.1, 2.3, 1.1])

metrics = evaluator.calculate_ranking_metrics(y_true, y_pred)
# Output: {'mse': 0.03, 'mae': 0.14, 'rmse': 0.17, 'r2_score': 0.99}

# Calcular NDCG (ranking)
ndcg = evaluator.calculate_ndcg(y_true, y_pred, k=3)

# Validar outputs del modelo
validation = validator.validate_model_output(
    predictions=np.array([0.5, 0.8, 0.3]),
    expected_shape=(3,),
    value_range=(0, 1)
)

# Detectar data drift
baseline_df = pd.DataFrame({'price': [10, 20, 30]})
current_df = pd.DataFrame({'price': [15, 25, 35]})

drift = validator.check_data_drift(baseline_df, current_df, threshold=0.1)
# Output: {'drift_detected': True, 'columns_with_drift': ['price'], ...}

# Generar reporte de evaluación
report = EvaluationReport("hybrid_ranker", "1.0.1")
report.add_metrics(metrics)
report.add_validation("data_drift", drift)
report_path = report.save()
```

#### Métricas Soportadas:

- **Ranking**: MSE, MAE, RMSE, R², NDCG, MRR
- **Clasificación**: Accuracy, Precision, Recall, F1-Score
- **Retrieval**: Precision, Recall, F1, Specificity, TP/FP/TN/FN
- **Data Quality**: Data drift detection

---

### 3. Monitoring Module (Monitoreo)

Recopila y analiza métricas en tiempo real.

#### Uso:

```python
from mlops import metrics_collector, anomaly_detector, health_monitor

# Registrar métricas
metrics_collector.record("api_latency_ms", 150.5)
metrics_collector.record("request_count", 1)
metrics_collector.record("error_rate", 0.02)

# Obtener estadísticas
stats = metrics_collector.get_stats("api_latency_ms", window_minutes=60)
# Output: {
#   'count': 250,
#   'mean': 145.3,
#   'std': 25.4,
#   'p95': 185.2,
#   'p99': 210.5
# }

# Detectar anomalías
values = np.array([10, 12, 11, 13, 100, 12, 11])
anomalies = anomaly_detector.detect_anomalies(values, threshold=3.0)
# Output: {
#   'anomalies': [{'index': 4, 'value': 100, 'z_score': 5.2}],
#   'anomaly_count': 1,
#   'anomaly_rate': 0.14
# }

# Detectar degradación de rendimiento
metrics = [0.92, 0.91, 0.90, 0.89, 0.85, 0.84, 0.83, 0.82, 0.80]
degraded = anomaly_detector.detect_performance_degradation(metrics, window_size=3)

# Verificar salud del sistema
health = health_monitor.get_system_status()
# Output: {
#   'timestamp': '2024-12-30T15:30:00.000000',
#   'overall_status': 'healthy',
#   'api': {...},
#   'checks': {'api_latency': true, 'error_rate': true}
# }
```

#### Métricas Recopiladas:

- `api_latency_ms` - Latencia de la API
- `translation_latency_ms` - Latencia de traducción
- `embedding_latency_ms` - Latencia de embeddings
- `num_recipes` - Número de recetas retornadas
- `request_count` - Total de solicitudes
- `error_rate` - Tasa de error (%)

---

### 4. Logging Module (Logging Estructurado)

Sistema centralizado de logging en formato JSON.

#### Uso:

```python
from mlops import get_logger, app_logger, mlops_logger, monitoring_logger

# Usar loggers predefinidos
app_logger.info("Application started")
mlops_logger.info("MLOps initialized")
monitoring_logger.warning("High latency detected")

# Crear logger estructurado personalizado
logger = get_logger(__name__)

# Log con contexto adicional
logger.log_with_context(
    level=logging.INFO,
    msg="Recommendation generated",
    extra_data={
        "request_id": "req_12345",
        "query": "chicken recipes",
        "latency_ms": 250.5,
        "status": "success"
    }
)
```

#### Archivos de Log:

- `logs/app_YYYYMMDD.log` - Logs de aplicación
- `logs/mlops_YYYYMMDD.log` - Logs de MLOps
- `logs/monitoring_YYYYMMDD.log` - Logs de monitoreo
- `logs/model_training_YYYYMMDD.log` - Logs de entrenamiento
- `logs/retraining_YYYYMMDD.log` - Logs de retraining

Formato JSON:
```json
{
  "timestamp": "2024-12-30T15:30:00.123456",
  "level": "INFO",
  "logger": "app",
  "message": "Recommendation generated",
  "module": "app",
  "function": "recommend_endpoint",
  "line": 245,
  "extra_data": {
    "request_id": "req_12345",
    "latency_ms": 250.5
  }
}
```

---

### 5. Retraining Module (Retraining Automático)

Pipeline para reentrenamiento automático de modelos.

#### Uso:

```python
from mlops import auto_scheduler, retraining_orchestrator
import pandas as pd

# Verificar si necesita retraining
needs_retrain, reasons = retraining_orchestrator.check_retrain_needed("hybrid_ranker")

# Programar retraining automático
results = auto_scheduler.check_and_schedule_retraining(["hybrid_ranker"])
# Output: {
#   'timestamp': '2024-12-30T15:30:00.000000',
#   'models_checked': 1,
#   'retraining_needed': [
#     {
#       'model_id': 'hybrid_ranker',
#       'reasons': {'time_interval': 'Deployed 10 days ago'}
#     }
#   ],
#   'scheduled_jobs': ['hybrid_ranker_1704045600.0']
# }

# Crear job de retraining
job = retraining_orchestrator.create_retrain_job("hybrid_ranker")

# Ejecutar retraining
training_data = pd.read_csv("training_data.csv")
validation_data = pd.read_csv("validation_data.csv")

success = retraining_orchestrator.execute_retrain(
    job=job,
    training_data=training_data,
    validation_data=validation_data
)

# Promover a producción
retraining_orchestrator.promote_to_production(
    "hybrid_ranker",
    job.new_version,
    approval_required=False
)

# Consultar estado de job
job_status = retraining_orchestrator.get_job_status(job.job_id)

# Listar jobs
all_jobs = retraining_orchestrator.list_jobs(model_id="hybrid_ranker", status="completed")
```

#### Condiciones de Retraining:

1. **Intervalo de tiempo** - Cada N días (configurable)
2. **Nuevos datos** - Cuando hay X muestras nuevas (configurable)
3. **Degradación de rendimiento** - Cuando accuracy cae > 5%

---

## 📡 API Endpoints Mejorados

### 1. Recomendaciones (Existente, Mejorado)

```bash
POST /recommend
Content-Type: application/json

{
  "query": "recetas con pollo"
}

Response:
{
  "recetas": [
    {
      "nombre": "Pollo al Horno",
      "descripción": "...",
      "ingredientes": ["pollo", "cebolla", "ajo"],
      "instrucciones": ["Precalentar horno..."],
      "calificación_promedio": 4.8
    }
  ]
}
```

### 2. Salud del Sistema

```bash
GET /health

Response:
{
  "timestamp": "2024-12-30T15:30:00.000000",
  "overall_status": "healthy",
  "api": {
    "api_status": "healthy",
    "latency_stats": {
      "mean": 145.3,
      "p95": 185.2,
      "p99": 210.5
    },
    "error_rate": 0.02
  },
  "checks": {
    "api_latency": true,
    "error_rate": true
  }
}
```

### 3. Métricas en Tiempo Real

```bash
GET /metrics?window_minutes=60

Response:
{
  "timestamp": 1735589400.123,
  "window_minutes": 60,
  "metrics": {
    "api_latency_ms": {
      "mean": 145.3,
      "std": 25.4,
      "min": 89.2,
      "max": 245.8,
      "p95": 185.2,
      "p99": 210.5
    },
    "error_rate": {
      "mean": 0.02,
      "max": 0.05
    }
  }
}
```

### 4. Listado de Modelos

```bash
GET /models

Response:
{
  "count": 3,
  "models": [
    {
      "model_key": "hybrid_ranker_1.0.0",
      "model_id": "hybrid_ranker",
      "version": "1.0.0",
      "status": "production",
      "metrics": {
        "accuracy": 0.92,
        "precision": 0.89
      },
      "deployment_date": "2024-12-25T10:00:00"
    }
  ]
}
```

### 5. Modelo en Producción

```bash
GET /models/{model_id}/production

Response:
{
  "model_id": "hybrid_ranker",
  "version": "1.0.0",
  "status": "production",
  "metrics": {...},
  "deployment_date": "2024-12-25T10:00:00"
}
```

### 6. Verificar Retraining Necesario

```bash
POST /retrain/check

Response:
{
  "timestamp": "2024-12-30T15:30:00.000000",
  "models_checked": 1,
  "retraining_needed": [
    {
      "model_id": "hybrid_ranker",
      "reasons": {
        "time_interval": "Deployed 10 days ago"
      }
    }
  ],
  "scheduled_jobs": ["hybrid_ranker_1704045600.0"]
}
```

---

## 🚀 Ejecutar la Aplicación

### Con Docker

```bash
docker build -t recipe-recommender .
docker run -p 8000:8000 \
  -e MLFLOW_TRACKING_URI=/app/mlruns \
  -e QDRANT_API_KEY=your_key \
  recipe-recommender
```

### Localmente

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Ver MLflow UI

```bash
mlflow ui --backend-store-uri ./mlruns
```

Accede a `http://localhost:5000` para ver el tracking de experimentos.

---

## 📈 Ejemplo de Flujo Completo

```python
"""
Ejemplo completo: Entrenar, evaluar y monitorear un modelo
"""

from mlops import (
    model_registry,
    ModelEvaluator,
    EvaluationReport,
    retraining_orchestrator,
    metrics_collector,
)
import pandas as pd
import numpy as np

# 1. Cargar datos
training_data = pd.read_csv("training_data.csv")

# 2. Entrenar modelo
# ... código de entrenamiento ...

# 3. Evaluar
evaluator = ModelEvaluator()
y_true = training_data['rating'].values
y_pred = model.predict(training_data)

metrics = evaluator.calculate_ranking_metrics(y_true, y_pred)
print(f"Metrics: {metrics}")

# 4. Generar reporte
report = EvaluationReport("hybrid_ranker", "1.0.1")
report.add_metrics(metrics)
report_path = report.save()

# 5. Registrar modelo
from mlops import ModelMetadata

metadata = ModelMetadata(
    model_id="hybrid_ranker",
    model_type="hybrid",
    version="1.0.1",
    description="Improved model with better accuracy",
    metrics=metrics,
    parameters={...},
    status="validation"
)

model_registry.register_model(metadata)

# 6. Monitorear en tiempo real (en producción)
metrics_collector.record("api_latency_ms", 145.3)
metrics_collector.record("request_count", 1)

# 7. Promocionar a producción
model_registry.update_model_status("hybrid_ranker", "1.0.1", "production")

# 8. Verificar salud
from mlops import health_monitor
status = health_monitor.get_system_status()
print(f"System status: {status}")
```

---

## 🔍 Troubleshooting

### Problema: MLflow UI no se abre

**Solución:**
```bash
mlflow ui --backend-store-uri ./mlruns --host 0.0.0.0 --port 5000
```

### Problema: Permisos en logs

**Solución:**
```bash
chmod 755 logs/
chmod 755 mlops/
```

### Problema: Imports fallan

**Solución:**
```bash
pip install -r requirements.txt --upgrade
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

---

## 📚 Referencias

- [MLflow Documentation](https://mlflow.org/docs)
- [MLOps Concepts](https://cloud.google.com/architecture/mlops-basics)
- [Structured Logging](https://www.python-json-logger.readthedocs.io/)
- [Model Versioning Best Practices](https://semver.org/)

---

## 👥 Contribuciones

Para agregar nuevas métricas o módulos:

1. Editar el módulo correspondiente en `mlops/`
2. Actualizar `mlops/__init__.py`
3. Agregar tests
4. Actualizar esta documentación

---

**Última actualización:** 30 de diciembre, 2024
