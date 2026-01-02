# MLOps - Estructura clara

Breve guía para evidenciar prácticas MLOps en este proyecto.

Estructura:
- `scripts/`: Implementaciones de scripts MLOps
  - `version_model.py`: registro/versionado de modelo (MLflow + fallback local).
  - `evaluate.py`: evaluación de modelo (pickle + CSV).
  - `evaluate_embeddings.py`: evaluación de embeddings (testembedding-3small simulado/OpenAI).
  - `evaluate_llm.py`: evaluación de LLMs (GPT4.1 simulado/OpenAI).
  - `monitor.py`: registro de eventos/métricas.
  - `retrain.py`: placeholder para retraining automático.
- Salidas (logs/registro):
  - `monitor.log`: registro de eventos de monitorización.
  - `model_versions.txt`: registro de versiones de modelos.
  - `artifacts/`: artefactos de evaluación (embeddings JSON, respuestas de LLM, etc.).

Uso rápido:

```bash
python -m mlops.scripts.version_model --model-path path/al/modelo.pkl --name MiModelo
python -m mlops.scripts.evaluate --model-path path/al/modelo.pkl --data data/test.csv
python -m pytest -q
```

O importar en Python:

```python
from mlops.scripts.evaluate_embeddings import evaluate
evaluate('testembedding-3small')
```

- Si quieres usar MLflow localmente para pruebas, puedes levantar un servidor de tracking local:

```bash
pip install mlflow
mkdir -p mlruns
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 127.0.0.1 --port 5000
```

Luego exporta la variable de entorno `MLFLOW_TRACKING_URI=http://127.0.0.1:5000` y ejecuta `version_model.py`.

CI / GitHub Actions:

- Este repositorio incluye un workflow de ejemplo en `.github/workflows/ci-mlops.yml` que ejecuta tests y arranca un servidor MLflow en CI para demostrar el registro de artefactos.

Mantener esto conciso: los scripts son minimalistas para evidenciar el flujo MLOps.
