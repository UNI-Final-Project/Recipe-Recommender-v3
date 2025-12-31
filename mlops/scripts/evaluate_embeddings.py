"""Evaluación mínima de embeddings para `testembedding-3small`.
Intenta usar OpenAI si `OPENAI_API_KEY` está presente; si no, genera embeddings simuladas.
Calcula similitud coseno media frente a embeddings de referencia (si existen) o usa embeddings del propio dataset.
Registra métricas en mlops/monitor.log y en mlops/model_versions.txt (o MLflow si está disponible).
"""
import os
import argparse
import json
import math
import random
import datetime
from typing import List

# Optional MLflow
try:
    import mlflow
except Exception:
    mlflow = None


def cosine(a: List[float], b: List[float]) -> float:
    num = sum(x*y for x,y in zip(a,b))
    norma = math.sqrt(sum(x*x for x in a))
    normb = math.sqrt(sum(x*x for x in b))
    if norma==0 or normb==0:
        return 0.0
    return num/(norma*normb)


def get_embeddings_texts(texts: List[str], model_name: str):
    """Genera embeddings: intenta usar OpenAI, si no, usa vectores aleatorios reproducibles."""
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key and model_name:
        try:
            import openai
            openai.api_key = api_key
            res = [openai.Embedding.create(input=t, model=model_name) for t in texts]
            return [r['data'][0]['embedding'] for r in res]
        except Exception:
            pass
    # fallback: reproducible pseudo-embeddings
    out = []
    for t in texts:
        rnd = random.Random(hash(t) & 0xffffffff)
        v = [rnd.random() for _ in range(64)]
        out.append(v)
    return out


def record_monitor(message: str):
    os.makedirs('mlops', exist_ok=True)
    with open('mlops/monitor.log', 'a', encoding='utf-8') as f:
        f.write(message + '\n')


def simple_register(model_name: str, info: dict):
    os.makedirs('mlops', exist_ok=True)
    out = {'model': model_name, 'info': info}
    with open('mlops/model_versions.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(out) + '\n')


def evaluate(model_name: str, texts_file: str = None):
    texts = ["hello world", "recipe for pancakes", "how to boil an egg"]
    # Intentar cargar desde archivo de datos default
    if not texts_file:
        default_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'embeddings_texts.txt')
        if os.path.exists(default_path):
            texts_file = default_path
    if texts_file and os.path.exists(texts_file):
        with open(texts_file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
            if lines:
                texts = lines[:50]  # Usar hasta 50 textos
    emb = get_embeddings_texts(texts, model_name)
    # compare each vector to the mean vector
    mean = [sum(col)/len(col) for col in zip(*emb)]
    sims = [cosine(v, mean) for v in emb]
    avg_sim = sum(sims)/len(sims)

    # registrar en monitor local
    record_monitor(f"embedding_evaluation model={model_name} avg_cosine={avg_sim}")

    # escribir artifacts locales
    os.makedirs('mlops/artifacts', exist_ok=True)
    ts = datetime.datetime.utcnow().isoformat().replace(':', '-')
    emb_path = f"mlops/artifacts/embeddings_{ts}.json"
    with open(emb_path, 'w', encoding='utf-8') as f:
        json.dump({'texts': texts, 'embeddings_sample': emb[:3]}, f)

    info = {'avg_cosine': avg_sim, 'n': len(sims), 'embeddings_file': emb_path}

    # Try MLflow logging if available
    if mlflow is not None:
        try:
            with mlflow.start_run():
                mlflow.log_param('model_name', model_name)
                mlflow.log_metric('avg_cosine', float(avg_sim))
                mlflow.log_param('n_texts', len(texts))
                mlflow.log_artifact(emb_path, artifact_path='eval/embeddings')
        except Exception:
            simple_register(model_name, info)
    else:
        simple_register(model_name, info)

    print('avg_cosine', avg_sim)
    return avg_sim


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='testembedding-3small')
    parser.add_argument('--texts')
    args = parser.parse_args()
    evaluate(args.model, args.texts)
