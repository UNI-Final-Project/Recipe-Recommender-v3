class DummyModel:
    def predict(self, X):
        # X puede ser DataFrame o lista-like
        try:
            n = len(X)
        except Exception:
            n = 1
        return [0] * n
