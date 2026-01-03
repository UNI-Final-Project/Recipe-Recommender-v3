# Resumen MLOps: Recipe Recommender v3

## Estado Actual (Secciones 5-8 Mejoradas)

Se ha completado la implementación de **MLOps completo** cubriendo:

### ✅ 5. Orquestación y Despliegue
- **CI/CD en GitHub Actions**: Tests automáticos + despliegue a Cloud Run
- **Versionado Python 3.11**: Alineado con Dockerfile
- **Smoke Tests**: Validación de sintaxis y funcionalidad básica
- **Docker Build & Push**: A Google Container Registry
- **Cloud Run Deploy**: Automático en push a main

### ✅ 6. Monitoreo y Mantenimiento
- **Logging Estructurado**: MLflow + Cloud Logging en `app.py`
- **Métricas Registradas**: `api_latency_ms`, `translation_latency_ms`, `num_recipes`
- **Alertas (Recomendadas)**: GCP Cloud Monitoring policies
- **Mantenimiento Preventivo**: Limpieza de artefactos antiguos

### ✅ 7. Evaluación de la Aplicación
- **Tests Unitarios**: `test_smoke.py` (sintaxis, imports)
- **Tests de Contrato**: `test_contracts.py` (validación Pydantic schemas)
- **Tests de Regresión**: `test_regression.py` (latencia P95, data quality)
- **Golden Tests**: Tests de determinismo LLM (recomendado implementar)

### ✅ 8. Resultados y Demostración
- **Matriz de Cumplimiento MLOps**: Versionado, CI/CD, logging, tests ✅
- **Demostración E2E**: Flujos local, GitHub Actions, Cloud Run
- **Documentación Completa**: Guías de setup, troubleshooting, comandos

---

## Comandos Rápidos (MLOps)

```bash
# Setup Local
mlflow server --backend-store-uri sqlite:///mlflow.db --port 5000 &
uvicorn app:app --reload

# Tests
pytest tests/ -v
pytest tests/test_contracts.py -v        # Schemas
pytest tests/test_regression.py -v -m slow  # Performance

# Versionado
python mlops/scripts/version_model.py --model-path food.pkl --name weekly-retrain

# Cloud Run
gcloud run logs read recipe-api --limit=50
gcloud run deploy recipe-api --image gcr.io/$PROJECT/recipe-api:$SHA --region us-central1
```

---

## Archivos Clave

| Archivo | Propósito |
|---------|----------|
| [MLOPS_SECTIONS_5-8.md](MLOPS_SECTIONS_5-8.md) | Detalle completo de secciones 5-8 (Orquestación, Monitoreo, Evaluación, Resultados) |
| [MLOPS_SETUP.md](MLOPS_SETUP.md) | Guía step-by-step: setup local, CI/CD, Cloud Run, troubleshooting |
| `.github/workflows/ci-mlops.yml` | Workflow: tests + deploy a Cloud Run con smoke tests |
| `tests/test_contracts.py` | Validación de schemas Pydantic (QueryIn, RecipeOut) |
| `tests/test_regression.py` | Latencia, data quality, score consistency |
| `mlops/scripts/version_model.py` | Registro de versiones (MLflow o local) |

---

## Próximos Pasos

1. **Validar Secrets en GitHub** (GCP_PROJECT, GCP_SA_KEY, etc.)
2. **Implementar Endpoints Faltantes** (/analyze-meal, /chat, /qa)
3. **Persistencia Conversacional** (Supabase table)
4. **Retraining Periódico** (scheduled workflow)
5. **Cloud Monitoring Alerts** (latencia, error rate)

---

MLOps para LLMs y Embeddings

```
mlops/
├── __init__.py               (paquete Python)
├── scripts/                  (implementaciones)
│   ├── __init__.py
│   ├── version_model.py      (versionado de modelos)
│   ├── evaluate.py           (evaluación de modelos)
│   ├── evaluate_embeddings.py (evaluación de embeddings, OpenAI o simulado)
│   ├── evaluate_llm.py       (evaluación de LLMs, OpenAI o simulado)
│   ├── monitor.py            (registro de eventos/métricas)
│   └── retrain.py            (placeholder para retraining)
├── artifacts/                (artefactos generados por evaluaciones)
├── monitor.log               (registro de eventos)
├── model_versions.txt        (registro de versiones de modelos)
└── README.md
```

Se añadieron scripts para evaluar y versionar:

- `mlops/scripts/evaluate_llm.py`: evaluación mínima para LLMs (p. ej. `gpt-4.1`). Intenta usar la API de OpenAI si `OPENAI_API_KEY` está presente; si no, ejecuta un modo simulado para permitir pruebas locales/CI.
- `mlops/scripts/evaluate_embeddings.py`: evaluación mínima para embeddings (p. ej. `testembedding-3small`) con cálculo de similitud coseno media.

Ambos scripts registran resultados en `mlops/monitor.log` y en `mlops/model_versions.txt` (o en MLflow si está disponible). Los tests automáticos en `tests/test_mlops_models.py` ejecutan estos scripts en modo simulado.

Métricas registradas:
- LLMs: `avg_response_len`, `n_prompts`
- Embeddings: `avg_cosine`, `n_texts`
- Artifacts en MLflow: prompts/respuestas, embeddings JSON
