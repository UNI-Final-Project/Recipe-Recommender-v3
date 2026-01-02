"""Script placeholder para disparar un retraining.
Intenta llamar a `src/train.py` si existe, o anota el intento en `mlops/retrain.log`.
"""
import subprocess
import os


def try_retrain():
    train_script = os.path.join('src', 'train.py')
    os.makedirs('mlops', exist_ok=True)
    if os.path.exists(train_script):
        try:
            print('Ejecutando retraining mediante src/train.py...')
            subprocess.check_call(["python", train_script])
            print('Retraining completado.')
            return 0
        except Exception as e:
            with open('mlops/retrain.log', 'a', encoding='utf-8') as f:
                f.write(f'Retrain failed: {e}\n')
            print('Error durante retraining, ver mlops/retrain.log')
            return 2
    else:
        with open('mlops/retrain.log', 'a', encoding='utf-8') as f:
            f.write('Retrain placeholder invoked (no se encontró src/train.py)\n')
        print('No hay script de entrenamiento; registrado placeholder en mlops/retrain.log')
        return 0


if __name__ == '__main__':
    exit(try_retrain())
