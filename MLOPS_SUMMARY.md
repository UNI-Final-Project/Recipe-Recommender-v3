Resumen MLOps (conciso)

Objetivos evidenciados:
- Versionado de modelos: `mlops/scripts/version_model.py` (registro local o MLflow).
- Evaluación: `mlops/scripts/evaluate.py` (evaluación mínima con CSV de test).
- Evaluación de embeddings: `mlops/scripts/evaluate_embeddings.py` (testembedding-3small).
- Evaluación de LLMs: `mlops/scripts/evaluate_llm.py` (gpt-4.1).
- Monitoreo / logging: `mlops/scripts/monitor.py` y `config/mlops.yaml` (ruta de logs).
- Retraining: `mlops/scripts/retrain.py` (placeholder que invoca `src/train.py` si existe).
- Organización: scripts en `mlops/scripts/`, salidas (logs/artefactos) en `mlops/`, configuración en `config/`, tests en `tests/`.

Comandos rápidos:

```bash
# Registrar versión (MLflow si está disponible)
python -m mlops.scripts.version_model --model-path path/al/modelo.pkl --name MiModelo

# Evaluar modelo
python -m mlops.scripts.evaluate --model-path path/al/modelo.pkl --data data/test.csv

# Evaluar embeddings
python -m mlops.scripts.evaluate_embeddings --model testembedding-3small

# Evaluar LLM
python -m mlops.scripts.evaluate_llm --model gpt-4.1

# Monitor: registrar un evento
python -m mlops.scripts.monitor --message "test metric=0.9"

# Ejecutar todos los tests
python -m pytest -q
```

MLflow y CI (breve):

- `requirements.txt` ya incluye `mlflow`.
- Para pruebas locales, levanta un servidor MLflow:

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 127.0.0.1 --port 5000
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
python -m mlops.scripts.version_model --model-path path/al/modelo.pkl --name LocalRun
```

- En CI, el workflow de ejemplo está en [.github/workflows/ci-mlops.yml](.github/workflows/ci-mlops.yml) — ejecuta tests, arranca un servidor MLflow y registra un artefacto de ejemplo.

MLOps para LLMs y Embeddings
--------------------------------

Estructura de carpetas:

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
