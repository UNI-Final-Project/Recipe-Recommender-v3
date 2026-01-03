# MLOps Documentation: Recipe Recommender

## Índice

1. [Setup Inicial](#setup-inicial)
2. [Flujo de Desarrollo Local](#flujo-de-desarrollo-local)
3. [CI/CD en GitHub Actions](#cicd-en-github-actions)
4. [Despliegue a Cloud Run](#despliegue-a-cloud-run)
5. [Monitoreo y Alertas](#monitoreo-y-alertas)
6. [Versionado y Reproducibilidad](#versionado-y-reproducibilidad)

---

## Setup Inicial

### Requisitos

- Python 3.11
- Docker
- Git
- Cuenta GCP (para despliegue)
- Llaves API: OpenAI, Qdrant Cloud

### Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/UNI-Final-Project/Recipe-Recommender-v3.git
cd Recipe-Recommender-v3

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env con llaves
cat > .env << EOF
OPENAI_API_KEY=sk-...
QDRANT_API_KEY=...
QDRANT_HOST=https://a48878a9-e5e9-4cf4-9283-...qdrant.io
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=recipe-recommendations
EOF
```

---

## Flujo de Desarrollo Local

### 1. Iniciar MLflow UI (Trazabilidad de Experimentos)

```bash
# Terminal 1: MLflow server
mkdir -p mlruns
mlflow server --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns --port 5000

# Visitar: http://localhost:5000
```

### 2. Ejecutar Aplicación

```bash
# Terminal 2: FastAPI server
uvicorn app:app --reload --port 8000
```

### 3. Hacer Pruebas

```bash
# Terminal 3: Petición de ejemplo
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "healthy pasta recipe"}'

# Respuesta esperada:
# {
#   "recetas": [
#     {
#       "nombre": "Whole Wheat Pasta with Vegetables",
#       "descripción": "...",
#       "ingredientes": [...],
#       "instrucciones": [...],
#       "calificación_promedio": 4.5
#     }
#   ]
# }
```

### 4. Ejecutar Tests Locales

```bash
# Tests básicos
pytest tests/test_smoke.py -v

# Tests de contrato (schemas Pydantic)
pytest tests/test_contracts.py -v

# Tests de regresión (performance)
pytest tests/test_regression.py -v -m slow

# Todos los tests con cobertura
pytest tests/ --cov=app --cov-report=html
```

---

## CI/CD en GitHub Actions

### Flujo Automático

**Disparadores:**
- `push` a `main` → Ejecuta test + deploy
- `pull request` a `main` → Solo test (sin deploy)

### Ver Logs de Acciones

```bash
# Opción 1: GitHub UI
# Ir a: Actions → [Workflow name] → [Run]

# Opción 2: CLI (si tienes gh instalado)
gh run list --limit 10
gh run view <RUN_ID> --log
```

### Pasos del Workflow

1. **Checkout & Setup Python 3.11**
2. **Cache pip** (acelera instalación)
3. **Install dependencies**
4. **Run tests** (pytest)
5. **Build Docker image** (solo en push a main)
6. **Push a Google Container Registry**
7. **Deploy a Cloud Run** (solo en push a main)

### Badge de Estado

El badge en [README.md](README.md) muestra el estado en tiempo real:

```markdown
[![CI - MLOps](https://github.com/UNI-Final-Project/Recipe-Recommender-v3/actions/workflows/ci-mlops.yml/badge.svg)](https://github.com/UNI-Final-Project/Recipe-Recommender-v3/actions/workflows/ci-mlops.yml)
```

---

## Despliegue a Cloud Run

### Configuración Previa (Una sola vez)

#### 1. Crear Proyecto GCP

```bash
export PROJECT_ID=recipe-recommender-prod
export REGION=us-central1
export SERVICE_NAME=recipe-api

gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID
```

#### 2. Habilitar APIs

```bash
gcloud services enable \
  run.googleapis.com \
  containerregistry.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com
```

#### 3. Crear Cuenta de Servicio

```bash
# Crear SA
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions CI/CD"

# Asignar roles necesarios
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/storage.admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser

# Generar JSON key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

#### 4. Configurar Secretos en GitHub

En **Settings → Secrets and variables → Actions**, agregar:

```
GCP_PROJECT = recipe-recommender-prod
GCP_REGION = us-central1
CLOUD_RUN_SERVICE = recipe-api
GCP_SA_KEY = <contenido de key.json>
```

#### 5. Crear Servicio en Cloud Run (Initial)

```bash
# Primera vez: crear servicio
gcloud run create $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:initial \
  --region $REGION \
  --memory 512Mi \
  --cpu 1 \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=$OPENAI_API_KEY"
```

### Deploy Manual (sin CI/CD)

```bash
# Build local
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$VERSION .

# Push a GCR
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:$VERSION

# Deploy
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$VERSION \
  --region $REGION
```

### Verificar Despliegue

```bash
# Ver URL del servicio
gcloud run services describe $SERVICE_NAME --region $REGION

# Hacer curl
curl https://<SERVICE-URL>/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "soup"}'

# Ver logs
gcloud run logs read $SERVICE_NAME --limit=50 --region $REGION
```

---

## Monitoreo y Alertas

### Ver Métricas en Cloud Monitoring

```bash
# Dashboard: GCP Console → Monitoring → Dashboards
# Crear nuevo dashboard con:
#  - API Latency (custom metric: recipe_api/latency_ms)
#  - Error Rate (HTTP 5xx)
#  - Cloud Run memory/CPU usage
```

### Crear Alert por Alta Latencia

```bash
# Via gcloud (o Console UI)
gcloud alpha monitoring policies create \
  --notification-channels=<CHANNEL_ID> \
  --display-name="Recipe API High Latency" \
  --condition-display-name="Latency > 3s" \
  --condition-threshold-value=3000 \
  --condition-threshold-duration=300s
```

### Habilitar Cloud Logging Avanzado

```python
# En app.py (con este código ya está incluido en version mejorada)
from google.cloud import logging as cloud_logging

cloud_client = cloud_logging.Client()
cloud_client.setup_logging()
```

---

## Versionado y Reproducibilidad

### MLflow Local

```bash
# Ver experimentos
mlflow ui

# Registrar modelo manualmente
python mlops/scripts/version_model.py \
  --model-path food_v2.pkl \
  --name "weekly-retrain"

# Ver versiones registradas
cat mlops/model_versions.txt
```

### Reproducibilidad

**Garantizada por:**
- Versionado de Python (3.11)
- Pinning de dependencias (`requirements.txt`)
- Versionado de datos (DVC + `food.pkl`)
- Versionado de modelos (MLflow)
- Configuración por entorno (`.env`)

### Rollback a Versión Anterior

```bash
# Si deployment tiene problemas
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:<PREVIOUS_SHA>

# Ver historial
gcloud run revisions list --service=$SERVICE_NAME --region=$REGION
```

---

## Troubleshooting

### Tests Fallan Localmente

```bash
# Limpiar caché
rm -rf __pycache__ .pytest_cache

# Reinstalar deps
pip install --upgrade --force-reinstall -r requirements.txt

# Ejecutar con verbosidad
pytest tests/ -vvv --tb=short
```

### Docker Build Falla en GCP

```bash
# Ver logs de build
gcloud builds log <BUILD_ID>

# Triggerar manual
gcloud builds submit --config=cloudbuild.yaml
```

### Cloud Run Timeout

```bash
# Aumentar timeout en deploy
gcloud run deploy $SERVICE_NAME \
  --timeout=600 \  # 10 minutos
  --memory=1Gi     # Aumentar memoria
```

### MLflow No Conecta

```bash
# Verificar servidor
curl http://localhost:5000

# Reiniciar
pkill -f "mlflow server"
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000
```

---

## Recursos

- [GitHub Actions Workflows Docs](https://docs.github.com/en/actions)
- [Cloud Run Deployment](https://cloud.google.com/run/docs/deploying)
- [MLflow Documentation](https://mlflow.org/docs/latest/)
- [FastAPI Production Guide](https://fastapi.tiangolo.com/deployment/)

---

**Última actualización:** 2 de enero de 2026
**Responsables:** Equipo MLOps Recipe Recommender

---

## Configurar Secrets en GitHub y re-ejecutar el workflow

Sigue estos pasos para añadir los secretos necesarios y volver a ejecutar el workflow de CI/CD que construye y despliega en Cloud Run.

1) Ir a: `Settings → Secrets and variables → Actions` en el repositorio de GitHub.

2) Crear los siguientes secrets (valores de ejemplo):

```
GCP_PROJECT = recipe-recommender-prod
GCP_REGION = us-central1
CLOUD_RUN_SERVICE = recipe-api
GCP_SA_KEY = <contenido del JSON de la service account>
```

Nota: `GCP_SA_KEY` debe ser el contenido exacto del archivo `key.json` generado con `gcloud iam service-accounts keys create`.

3) Confirmar que los secrets existen (desde la UI verás que están guardados).

4) Re-ejecutar el workflow:

- Opción A (re-run desde GitHub): Ir a `Actions → CI - MLOps → [Run]` y seleccionar "Re-run jobs".
- Opción B (trigger por push): Hacer un commit trivial y push en la rama (por ejemplo, actualizar README):

```bash
git commit --allow-empty -m "ci: trigger workflow" 
git push origin HEAD
```

5) Qué comprobar en la ejecución:

- `test` job: debe pasar pytest.
- `mlflow-register` job: debe ejecutar `python mlops/scripts/version_model.py ...` sin error de archivo no encontrado.
- `deploy` job: debe validar los secrets, establecer `IMAGE` y construir la imagen Docker con tag `gcr.io/<PROJECT>/<SERVICE>:<SHA>`.

6) En caso de error:

- Si `mlops/scripts/version_model.py` no se encuentra: confirmar que el archivo existe en la rama y ruta `mlops/scripts/version_model.py`.
- Si el tag de Docker aparece vacío: confirmar `GCP_PROJECT` y `CLOUD_RUN_SERVICE` están correctamente definidos.
- Consultar logs desde la UI de Actions o con `gh run view <RUN_ID> --log`.

7) Validación final en Cloud Run (si deploy pasa):

```bash
SERVICE_URL=$(gcloud run services describe $CLOUD_RUN_SERVICE --region $GCP_REGION --format 'value(status.url)')
curl -X POST $SERVICE_URL/recommend -H "Content-Type: application/json" -d '{"query":"tomato soup"}'
```

Con esto el flujo de registro y despliegue debería resolver los errores previos y crear un tag válido para la imagen Docker.
