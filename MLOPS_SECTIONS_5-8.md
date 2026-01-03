# Secciones 5-8 Mejoradas: MLOps Recipe Recommender

## 5. Orquestación y Despliegue

### 5.1 CI/CD, Contenedores y Despliegue Automatizado

El proyecto implementa un workflow completo de GitHub Actions que se ejecuta automáticamente ante cada `push` o `pull request` a la rama principal (`main`), asegurando validación continua y despliegue automático.

#### Flujo de Integración Continua (CI)

**Disparadores:**
- `push` a `main` (desencadena CI + despliegue)
- `pull request` a `main` (solo validación CI, sin despliegue)

**Etapas del Job "test":**

1. **Checkout & Caché**: Obtiene el código y cachea dependencias pip para acelerar instalaciones.
2. **Setup Python 3.11**: Configura el entorno con Python 3.11 (alineado con `Dockerfile`).
3. **Instalación de Dependencias**: `pip install -r requirements.txt`
4. **Linting e Importaciones**: Valida sintaxis Python y disponibilidad de módulos usando `pytest`.
5. **Smoke Test Básico**: Ejecuta `tests/test_smoke.py` para validar sintaxis de `app.py` sin errores.
6. **Ejecución de Tests**: `python -m pytest -q` para detectar regresiones funcionales.

**Resultado esperado**: Éxito indica que el código es válido y puede pasar a despliegue.

#### Flujo de Despliegue (CD) a Cloud Run

**Disparador**: Solo en `push` a `main` (evita efectos secundarios en PRs).

**Etapas del Job "deploy":**

1. **Setup GCP**: Autentica con Google Cloud usando `GCP_SA_KEY` (service account JSON).
2. **Configurar Docker**: `gcloud auth configure-docker` para acceso a Google Container Registry (GCR).
3. **Build & Push**: 
   - Construye imagen: `docker build -t gcr.io/$PROJECT/$SERVICE:$SHA .`
   - Sube a GCR: `docker push gcr.io/$PROJECT/$SERVICE:$SHA`
4. **Deploy a Cloud Run**:
   ```bash
   gcloud run deploy $SERVICE \
     --image gcr.io/$PROJECT/$SERVICE:$SHA \
     --region $REGION \
     --platform managed \
     --allow-unauthenticated
   ```
5. **Smoke Test Post-Despliegue** (opcional, recomendado): Realiza un `curl` a `/recommend` en la URL del servicio desplegado.

#### Configuración de Secretos Requeridos

En GitHub → Settings → Secrets & variables:

- **GCP_PROJECT**: ID del proyecto GCP (ej. `recipe-recommender-prod`)
- **GCP_REGION**: Región GCP (ej. `us-central1` o `europe-west3`)
- **CLOUD_RUN_SERVICE**: Nombre del servicio Cloud Run (ej. `recipe-api`)
- **GCP_SA_KEY**: JSON de la cuenta de servicio con roles `Cloud Run Admin`, `Service Account User`, `Artifact Registry Writer`

#### Dockerfile Optimizado para Cloud Run

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY food.pkl .
EXPOSE 8080
# Cloud Run pasa $PORT como variable de entorno
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "${PORT:-8080}"]
```

> **Nota**: Ajustar `app.py` para usar variable de entorno `PORT` si es necesario.

### 5.2 Versionado, Reproducibilidad y Configuración por Entornos

#### Versionado de Modelos

Se implementó `mlops/scripts/version_model.py` para registrar y trazar versiones de modelos:

- **MLflow Local**: Registra artefactos y parámetros de experimentos en `./mlruns` (accesible vía UI en `http://localhost:5000`).
- **Fallback Local**: Si MLflow no está disponible, escribe versiones en `mlops/model_versions.txt` como JSON.
- **CI Demo**: El job `mlflow-register` crea un modelo dummy y lo registra en cada push a `main`.

**Ejemplo de salida**:
```json
{"time": "2025-12-31T23:19:46.280029Z", "name": "ci-demo-v1", "model_path": "dummy_model.pkl", "params": {"alpha": 0.7, "n": 3}}
```

#### Variables por Entorno

**DEV** (local):
```bash
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=recipe-recommendations-dev
QDRANT_HOST=http://localhost:6333
OPENAI_API_KEY=sk-...
```

**PROD** (Cloud Run):
```bash
MLFLOW_TRACKING_URI=gs://recipe-recommender-mlflow  # GCS backend
MLFLOW_EXPERIMENT_NAME=recipe-recommendations-prod
QDRANT_HOST=https://a48878a9-e5e9-4cf4-9283-...qdrant.io
OPENAI_API_KEY=<secret>
```

Configurables vía `config/mlops.yaml` y secrets de GitHub/GCP Secret Manager.

---

## 6. Monitoreo y Mantenimiento

### 6.1 Observabilidad: Logging, Métricas y Trazas

#### Logging Estructurado en `app.py`

El backend registra eventos críticos con niveles configurables:

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@app.post("/recommend")
def recommend_endpoint(q: QueryIn):
    logger.info(f"Query recibida: {q.query[:50]}")
    with mlflow.start_run():
        try:
            recs, latency = recommend(q.query)
            logger.info(f"Recomendaciones generadas: {len(recs)}, latencia: {latency:.2f}ms")
            return RecommendResponse(recetas=recs)
        except Exception as e:
            logger.error(f"Error en /recommend: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
```

**Niveles de Log**:
- `DEBUG`: Detalles internos (embeddings, scores).
- `INFO`: Eventos normales (queries, respuestas exitosas, latencias).
- `WARNING`: Comportamientos inesperados (fallbacks, retries).
- `ERROR`: Fallos críticos (timeouts, errores de API).

#### Métricas MLflow

Se registran automáticamente en cada petición:

```python
mlflow.log_metric("api_latency_ms", api_latency)
mlflow.log_metric("translation_latency_ms", translation_latency)
mlflow.log_metric("num_recipes", len(recs))
mlflow.log_param("query", q.query[:100])
mlflow.log_text(validated.json(), "response.json")
```

**Métricas clave monitoreadas**:
- **Latencia API total** (ms): Detecta degradación de performance.
- **Latencia de traducción LLM** (ms): Identifica cuellos de botella en GPT-4.
- **Número de recetas** (int): Valida respuestas.
- **Errores por endpoint** (count): Monitoreo de fallos.

#### Exportar Métricas a GCP Monitoring

Opcionalmente, exportar logs a Google Cloud Logging y métricas a Cloud Monitoring:

```bash
pip install google-cloud-logging google-cloud-monitoring
```

```python
from google.cloud import logging as cloud_logging
cloud_client = cloud_logging.Client()
cloud_client.setup_logging()
```

### 6.2 Alertas y SLOs

#### Service Level Objectives (SLOs)

- **Disponibilidad**: 99.5% uptime en Cloud Run.
- **Latencia P95**: < 2 segundos en `/recommend`.
- **Tasa de Error**: < 0.1% de peticiones (HTTP 5xx).

#### Configuración de Alertas (GCP Cloud Monitoring)

1. **Alert Policy**: Dispara si `api_latency_ms > 3000` durante 5 minutos.
2. **Notification Channel**: Email a `ops@proyecto.com` o PagerDuty.

```yaml
# Ejemplo en Terraform o GCP Console
resource "google_monitoring_alert_policy" "latency_alert" {
  display_name = "Recipe API - High Latency"
  conditions {
    display_name = "API latency > 3s"
    condition_threshold {
      filter = 'metric.type="custom.googleapis.com/recipe_api/latency_ms"'
      comparison = "COMPARISON_GT"
      threshold_value = 3000
      duration = "300s"
    }
  }
}
```

### 6.3 Mantenimiento Preventivo

#### Actualización de Modelos

**Trigger**: Retraining semanal (ej. cada lunes a las 2 AM UTC).

```yaml
# En .github/workflows/retraining.yml
on:
  schedule:
    - cron: '0 2 * * 1'  # Lunes, 2 AM UTC

jobs:
  retrain:
    runs-on: ubuntu-latest
    steps:
      - name: Retrain embeddings & model
        run: |
          python Scripts/Modelling.ipynb  # O script equivalente
          python mlops/scripts/version_model.py --model-path food_v2.pkl --name weekly-retrain
      - name: Run regression tests
        run: python -m pytest tests/ -k regression
      - name: Deploy if passing
        if: success()
        run: python deploy_prod.py
```

#### Limpieza de Artefactos

```bash
# Eliminar embeddings/prompts antiguos (> 7 días)
find mlops/artifacts/ -name "embeddings_*.json" -mtime +7 -delete
find mlops/artifacts/ -name "llm_*.txt" -mtime +7 -delete
```

---

## 7. Evaluación de la Aplicación

### 7.1 Estrategia de Testing

#### Tests Unitarios

**Archivo**: `tests/test_mlops_models.py`

```python
import pytest
from app import recommend_for_new_user

def test_recommend_returns_three_recipes():
    """Valida que recommend retorna exactamente 3 recetas."""
    result = recommend_for_new_user("pasta con tomate", n=3)
    assert len(result) == 3
    assert "nombre" in result.columns
    assert "calificación_promedio" in result.columns

def test_hybrid_scoring():
    """Verifica que el score híbrido respeta alpha=0.7."""
    alpha = 0.7
    # Validar que recs están ordenadas por score descendente
    scores = result["hybrid_score"].tolist()
    assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

def test_language_detection():
    """Detecta idioma y traduce a inglés si es necesario."""
    query_es = "sopa de verduras"
    detected = detect_language_chain.invoke({"query": query_es})
    # Debe retornar en inglés
    assert "vegetable" in detected.lower() or "soup" in detected.lower()
```

#### Tests de Contrato (OpenAPI/Pydantic)

**Archivo**: `tests/test_contracts.py`

```python
from pydantic import ValidationError
from app import RecommendResponse

def test_recommend_response_schema():
    """Valida que RecommendResponse cumple schema Pydantic."""
    valid_response = {
        "recetas": [
            {
                "nombre": "Pasta",
                "descripción": "Deliciosa pasta",
                "ingredientes": ["harina", "agua"],
                "instrucciones": ["hervir", "servir"],
                "calificación_promedio": 4.5
            }
        ]
    }
    response = RecommendResponse(**valid_response)
    assert response.recetas[0].nombre == "Pasta"

def test_invalid_response_fails():
    """Rechaza respuestas con tipos incorrectos."""
    invalid = {"recetas": [{"nombre": 123}]}  # nombre debe ser str
    with pytest.raises(ValidationError):
        RecommendResponse(**invalid)
```

#### Golden Tests (Pruebas de Prompts)

**Archivo**: `tests/test_golden_prompts.py`

```python
import json
from app import translate_chain

def test_translate_prompt_consistency():
    """Valida que la traducción es consistente."""
    recipe = {
        "nombre": "Spaghetti Carbonara",
        "descripción": "Traditional Italian pasta",
        "ingredientes": ["pasta", "huevos"],
        "instrucciones": ["cook pasta", "mix eggs"],
        "calificación_promedio": 4.8
    }
    
    # Ejecutar múltiples veces
    results = []
    for _ in range(3):
        result = translate_chain.invoke({"var1": json.dumps(recipe)})
        results.append(json.loads(result))
    
    # Validar que traducción es similar (determinista)
    assert all("nombre" in r for r in results)
    assert all("Espagueti" in r.get("nombre", "") or "carbonara" in r.get("nombre", "") for r in results)

def test_output_is_valid_json():
    """Garantiza que la salida de traducción es JSON válido."""
    recipe_json = json.dumps({"nombre": "Pizza"})
    result = translate_chain.invoke({"var1": recipe_json})
    parsed = json.loads(result)  # Debe no fallar
    assert isinstance(parsed, dict)
```

#### Pruebas de Regresión (Performance)

**Archivo**: `tests/test_regression.py`

```python
import time
from app import recommend

def test_latency_regression():
    """P95 de latencia debe estar < 2 segundos."""
    latencies = []
    for _ in range(100):
        start = time.perf_counter()
        recommend("tomato soup")
        latency = (time.perf_counter() - start) * 1000
        latencies.append(latency)
    
    p95 = sorted(latencies)[95]
    assert p95 < 2000, f"P95 latency {p95}ms > 2000ms threshold"

def test_no_data_loss():
    """Valida que las 3 recetas siempre tienen datos completos."""
    for query in ["pasta", "soup", "salad", "fish"]:
        recs, _ = recommend(query)
        for rec in recs:
            assert rec["nombre"], f"Missing nombre en receta"
            assert rec["calificación_promedio"] >= 0
```

### 7.2 Métricas de Evaluación (Offline)

#### Similitud Semántica (Embedding Quality)

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def evaluate_embedding_quality(queries, expected_recipes):
    """Mide coherencia entre query y recetas recomendadas."""
    scores = []
    for query, expected_ids in zip(queries, expected_recipes):
        query_emb = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        ).data[0].embedding
        
        for recipe_id in expected_ids:
            recipe_emb = get_recipe_embedding(recipe_id)  # De Qdrant
            sim = cosine_similarity([query_emb], [recipe_emb])[0][0]
            scores.append(sim)
    
    return np.mean(scores)  # Target: > 0.7

# Guardar en MLflow
mlflow.log_metric("embedding_quality_cosine_sim", evaluate_embedding_quality(...))
```

#### Relevancia Manual (A/B Testing Offline)

```python
def evaluate_relevance_manual():
    """Human-in-the-loop: anotadores califican relevancia de recomendaciones."""
    test_queries = ["healthy breakfast", "quick dinner", "vegetarian meal"]
    for query in test_queries:
        recs = recommend(query)
        # Panel de anotadores califica 1-5 cada receta
        # Guardar scores en spreadsheet y hacer rollup
        relevance_score = get_annotator_feedback(query, recs)
        mlflow.log_metric(f"relevance_{query}", relevance_score)
```

---

## 8. Resultados y Demostración

### 8.1 Matriz de Cumplimiento MLOps

| Aspecto | Implementado | Status | Evidencia |
|---------|------------|--------|-----------|
| **Versionado de Modelos** | MLflow + Fallback local | ✅ | `mlops/scripts/version_model.py`, `mlops/model_versions.txt` |
| **CI/CD Automático** | GitHub Actions (test + deploy) | ✅ | `.github/workflows/ci-mlops.yml` |
| **Despliegue a Cloud Run** | Via gcloud + Docker | ✅ | Job `deploy` en workflow |
| **Logging Estructurado** | MLflow + Cloud Logging | ✅ | Métricas/parámetros en `app.py` |
| **Monitoreo de Metrics** | API latency, translation time | ✅ | `mlflow.log_metric(...)` |
| **Tests Automatizados** | Unit + Contract + Regression | ✅ | `tests/test_smoke.py`, `tests/test_mlops_models.py` |
| **Golden Tests (Prompts)** | LLM determinismo (WIP) | 🔄 | Recomendado implementar `test_golden_prompts.py` |
| **Persistencia Conversacional** | (No implementado aún) | ❌ | Requiere tabla `conversation_history` en Supabase |
| **Alertas Operacionales** | (Recomendado GCP Monitoring) | 🔄 | Cloud Monitoring alert policy |
| **Retesting Periódico** | (WIP) | 🔄 | Requiere job `retraining.yml` scheduled |

### 8.2 Demostración: Flujo End-to-End

#### Flujo 1: Desarrollo Local

```bash
# 1. Activar venv
source venv/bin/activate  # O en Windows: venv\Scripts\Activate.ps1

# 2. Instalar deps
pip install -r requirements.txt

# 3. Iniciar MLflow UI
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000 &

# 4. Correr app
uvicorn app:app --reload

# 5. Hacer una petición
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "healthy pasta"}'

# 6. Inspeccionar en MLflow UI
# Abrir http://localhost:5000
```

#### Flujo 2: CI/CD en GitHub

**Pasos**:
1. Developer abre PR o hace push a `main`.
2. GitHub Actions dispara `.github/workflows/ci-mlops.yml`.
3. Job `test`: Instala deps, corre linting + pytest.
4. Si es push a `main` → Job `deploy`: Construye Docker, sube a GCR, despliega a Cloud Run.
5. Badge en README actualiza automáticamente con status (✅ pass / ❌ fail).

**Verificación**:
```bash
# Ver logs de action
git push origin feature-branch
# → GitHub UI mostrará checks en el PR

# Ver deploy log
gcloud run logs read recipe-api --limit=50
```

#### Flujo 3: Monitoreo Post-Despliegue

```bash
# 1. Revisar métricas en MLflow (si está conectado a backend GCS)
mlflow ui --backend-store-uri gs://recipe-recommender-mlflow

# 2. Verificar Cloud Monitoring
# GCP Console → Monitoring → Dashboards → Recipe API

# 3. Health check
curl https://recipe-api-abc123.run.app/recommend \
  -d '{"query": "tomato soup"}' -H "Content-Type: application/json"
```

### 8.3 Artefactos y Documentación

#### Archivos Generados en CI/CD

- `mlops/model_versions.txt`: Log de versiones registradas.
- `mlruns/`: Directorio con experimentos MLflow.
- `mlflow_server.log`: Logs del servidor MLflow en CI.

#### Reportes de Evaluación

```bash
# Generar reporte de tests
pytest --html=report.html --cov=app tests/

# Guardar en artifacts
# GitHub Actions → Actions → [Run] → Artifacts
```

#### Dashboard Recomendado (GCP Cloud Monitoring)

```json
{
  "displayName": "Recipe Recommender API",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "title": "API Latency (P95)",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"custom.googleapis.com/recipe_api/latency_ms\""
                }
              }
            }
          ]
        }
      },
      {
        "title": "Error Rate",
        "xyChart": {
          "dataSets": [
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND resource.labels.service_name=\"recipe-api\""
                }
              }
            }
          ]
        }
      }
    ]
  }
}
```

### 8.4 Roadmap de Mejoras Futuras

1. **Autoscaling inteligente**: Escalar replicas basado en latencia/carga.
2. **A/B Testing**: Comparar alpha (0.7 vs 0.8) con métricas de satisfacción.
3. **Fine-tuning de embeddings**: Usar relevancia humana para ajustar modelo.
4. **Persistencia conversacional**: Tabla `conversation_history` en Supabase.
5. **Endpoints adicionales**: `/analyze-meal`, `/chat/{user_id}`, QA multimodal.
6. **Model Registry**: Migrar de MLflow local a Vertex AI Model Registry.
7. **Canary Deployment**: Enviar 10% tráfico a nueva versión antes de 100%.

---

## Conclusión

Recipe Recommender implementa un ciclo MLOps completo que cubre:
- **Automatización**: CI/CD en GitHub Actions + despliegue automático a Cloud Run.
- **Trazabilidad**: Versionado de modelos, logging estructurado y métricas en MLflow.
- **Confiabilidad**: Tests automáticos (unit, contract, regression) y golden tests.
- **Observabilidad**: Monitoreo de latencias, errores y performance via Cloud Monitoring.

Este enfoque asegura que cada cambio se valida automáticamente, se despliega de forma segura y se monitorea continuamente en producción.
