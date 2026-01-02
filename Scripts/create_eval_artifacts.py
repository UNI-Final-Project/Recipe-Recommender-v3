import pickle
import csv

class DummyModel:
    def predict(self, X):
        return [0] * len(X)

# Crear modelo serializado
with open('model_eval.pkl', 'wb') as f:
    pickle.dump(DummyModel(), f)

# Crear CSV de test
with open('data_test.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['feature','label'])
    writer.writerow([1,0])
    writer.writerow([2,0])

print('Creado model_eval.pkl y data_test.csv')
