"""Registro/versionado mínimo de modelos.
Intenta usar MLflow si está instalado; si no, registra versiones en `mlops/model_versions.txt`.
"""
import argparse
import datetime
import os
import json


def write_local_version(model_path, name, params=None):
    os.makedirs('mlops', exist_ok=True)
    out = {
        'time': datetime.datetime.utcnow().isoformat() + 'Z',
        'name': name,
        'model_path': model_path,
        'params': params or {}
    }
    with open('mlops/model_versions.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(out) + "\n")
    print('Versión registrada localmente en mlops/model_versions.txt')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', required=True)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()

    try:
        import mlflow
        from mlflow import pyfunc
        client = mlflow.tracking.MlflowClient()
        run_id = client.create_run(experiment_id='0').info.run_id
        mlflow.log_param('model_name', args.name)
        mlflow.log_artifact(args.model_path, artifact_path='model')
        print('Modelo registrado en MLflow (experimento 0).')
    except Exception:
        write_local_version(args.model_path, args.name)


if __name__ == '__main__':
    main()
