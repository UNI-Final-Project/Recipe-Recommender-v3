"""Script de evaluación mínimo.
Si dispone de `pandas` y un modelo serializado (pickle), calcula una métrica simple.
"""
import argparse
import os
import pickle


def simple_evaluate(model_path, data_path=None):
    if not os.path.exists(model_path):
        print('Modelo no encontrado:', model_path)
        return 2
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
    except Exception as e:
        print('No se pudo cargar el modelo:', e)
        return 2

    if data_path and os.path.exists(data_path):
        try:
            import pandas as pd
            from sklearn.metrics import accuracy_score
            df = pd.read_csv(data_path)
            if 'label' in df.columns and 'feature' in df.columns:
                X = df[['feature']]
                y = df['label']
                preds = model.predict(X)
                acc = accuracy_score(y, preds)
                print('Accuracy:', acc)
                return 0
            else:
                print('CSV de evaluación no tiene las columnas esperadas (feature,label).')
                return 1
        except Exception as e:
            print('Pandas/sklearn no disponibles o error al evaluar:', e)
            return 1
    else:
        print('Modelo cargado correctamente. No hay datos de evaluación proporcionados.')
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', required=True)
    parser.add_argument('--data', dest='data', required=False)
    args = parser.parse_args()
    exit(simple_evaluate(args.model_path, args.data))
