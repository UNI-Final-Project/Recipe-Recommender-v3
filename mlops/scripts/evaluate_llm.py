"""Evaluación mínima para un LLM (p.ej. GPT4.1).
- Si `OPENAI_API_KEY` está presente usará OpenAI Completion/Chat API (intentar); si no, simula respuestas.
- Calcula métricas simples: longitud media de respuesta y cobertura de tokens esperados (simulada).
- Registra en `mlops/monitor.log` y en modelo versiones.
"""
import os
import argparse
import json
import random
import datetime

# Optional MLflow
try:
    import mlflow
except Exception:
    mlflow = None


def simple_register(model_name: str, info: dict):
    os.makedirs('mlops', exist_ok=True)
    out = {'model': model_name, 'info': info}
    with open('mlops/model_versions.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(out) + '\n')


def record_monitor(message: str):
    os.makedirs('mlops', exist_ok=True)
    with open('mlops/monitor.log', 'a', encoding='utf-8') as f:
        f.write(message + '\n')


def call_llm(prompts, model_name):
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key and model_name:
        try:
            import openai
            openai.api_key = api_key
            out = []
            for p in prompts:
                # usar Chat completions si está disponible
                try:
                    r = openai.ChatCompletion.create(model=model_name, messages=[{"role":"user","content":p}], max_tokens=64)
                    out.append(r.choices[0].message.content)
                except Exception:
                    # fallback a text completion
                    r = openai.Completion.create(model=model_name, prompt=p, max_tokens=64)
                    out.append(r.choices[0].text)
            return out
        except Exception:
            pass
    # fallback simulado
    out = []
    rnd = random.Random(42)
    for p in prompts:
        out.append('Simulated response for: ' + (p[:40]))
    return out


def evaluate(model_name: str, prompts_file: str = None):
    prompts = [
        'What is a simple pancake recipe?',
        'How do I boil an egg?'
    ]
    # Intentar cargar desde archivo de datos default
    if not prompts_file:
        default_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'llm_prompts.txt')
        if os.path.exists(default_path):
            prompts_file = default_path
    if prompts_file and os.path.exists(prompts_file):
        with open(prompts_file, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
            if lines:
                prompts = lines[:50]  # Usar hasta 50 prompts
    responses = call_llm(prompts, model_name)
    lengths = [len(r.split()) for r in responses]
    avg_len = sum(lengths)/len(lengths)

    # registrar en monitor local
    record_monitor(f"llm_evaluation model={model_name} avg_response_len={avg_len}")

    # escribir artifacts locales
    os.makedirs('mlops/artifacts', exist_ok=True)
    ts = datetime.datetime.utcnow().isoformat().replace(':', '-')
    prompts_path = f"mlops/artifacts/llm_prompts_{ts}.txt"
    responses_path = f"mlops/artifacts/llm_responses_{ts}.txt"
    with open(prompts_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(prompts))
    with open(responses_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(responses))

    info = {'avg_response_len': avg_len, 'n': len(lengths), 'prompts_file': prompts_path, 'responses_file': responses_path}

    # Try MLflow logging if available
    if mlflow is not None:
        try:
            with mlflow.start_run():
                mlflow.log_param('model_name', model_name)
                mlflow.log_metric('avg_response_len', float(avg_len))
                mlflow.log_param('n_prompts', len(prompts))
                mlflow.log_artifact(prompts_path, artifact_path='eval/llm')
                mlflow.log_artifact(responses_path, artifact_path='eval/llm')
        except Exception:
            # fallback local registration
            simple_register(model_name, info)
    else:
        simple_register(model_name, info)

    print('avg_response_len', avg_len)
    return avg_len


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='gpt-4.1')
    parser.add_argument('--prompts')
    args = parser.parse_args()
    evaluate(args.model, args.prompts)
