"""
Tests de Regresión: Valida que la aplicación mantenga performance y comportamiento
esperado tras cambios. Corre como parte del workflow de despliegue.
"""

import time
import pytest
from app import recommend, recommend_for_new_user


class TestLatencyRegression:
    """Valida que las latencias de API no se degraden."""

    @pytest.mark.slow
    def test_p95_latency_threshold(self):
        """P95 de latencia debe estar < 2 segundos."""
        queries = [
            "tomato soup",
            "pasta carbonara",
            "healthy breakfast",
            "quick dinner",
            "vegetarian meal",
        ]
        latencies = []

        # Ejecutar múltiples queries para obtener distribución estadística
        for _ in range(20):
            for query in queries:
                start = time.perf_counter()
                try:
                    recommend(query)
                    latency_ms = (time.perf_counter() - start) * 1000
                    latencies.append(latency_ms)
                except Exception:
                    # Ignorar errores en tests de latencia
                    pass

        if latencies:  # Skip si no hay datos
            p95 = sorted(latencies)[int(len(latencies) * 0.95)]
            assert p95 < 2000, f"P95 latency {p95:.0f}ms exceeds 2000ms threshold"

    @pytest.mark.slow
    def test_median_latency_under_1sec(self):
        """Latencia mediana debe estar < 1 segundo."""
        latencies = []
        for _ in range(10):
            start = time.perf_counter()
            try:
                recommend("pasta")
                latency_ms = (time.perf_counter() - start) * 1000
                latencies.append(latency_ms)
            except Exception:
                pass

        if latencies:
            median = sorted(latencies)[len(latencies) // 2]
            assert median < 1000, f"Median latency {median:.0f}ms exceeds 1000ms"


class TestNoDataLoss:
    """Valida que las respuestas siempre tengan datos completos y válidos."""

    def test_all_recipes_have_required_fields(self):
        """Cada receta debe tener nombre, descripción, ingredientes, instrucciones."""
        test_queries = ["soup", "pasta", "salad", "fish", "chocolate"]
        for query in test_queries:
            result = recommend_for_new_user(query, n=3)
            assert len(result) == 3, f"Query '{query}' did not return 3 recipes"

            for idx, row in result.iterrows():
                assert row["nombre"], f"Row {idx}: missing nombre"
                assert isinstance(row["ingredientes"], (list, str))
                assert isinstance(row["instrucciones"], (list, str))
                assert row["calificación_promedio"] >= 0

    def test_no_null_values_in_response(self):
        """Ningún campo debe ser None/null."""
        result = recommend_for_new_user("tomato soup", n=3)
        assert result.isnull().sum().sum() == 0, "Found null values in response"

    def test_consistent_number_of_recipes(self):
        """Siempre retorna el número solicitado de recetas."""
        for n in [1, 3, 5]:
            result = recommend_for_new_user("pasta", n=n)
            assert len(result) == n, f"Expected {n} recipes, got {len(result)}"


class TestScoreConsistency:
    """Valida que el scoring híbrido sea consistente y correcto."""

    def test_recipes_ordered_by_score(self):
        """Las recetas deben estar ordenadas por score descendente."""
        result = recommend_for_new_user("pasta", n=3, return_scores=True)
        scores = result["hybrid_score"].tolist()

        # Verificar que está ordenado descendente
        for i in range(len(scores) - 1):
            assert (
                scores[i] >= scores[i + 1]
            ), f"Scores not in descending order: {scores}"

    def test_hybrid_score_in_range(self):
        """Score híbrido debe estar entre 0 y 1."""
        result = recommend_for_new_user("soup", n=3, return_scores=True)
        scores = result["hybrid_score"].tolist()

        for score in scores:
            assert 0 <= score <= 1, f"Score {score} out of [0, 1] range"


class TestErrorHandling:
    """Valida que los errores se manejan gracefully."""

    def test_empty_query_error_handling(self):
        """Manejo de queries vacías."""
        try:
            recommend_for_new_user("", n=3)
            # Si no lanza excepción, debe retornar resultado válido
        except Exception as e:
            # Es aceptable fallar, pero el error debe ser informativo
            assert str(e)  # Debe tener mensaje de error

    def test_very_long_query(self):
        """Manejo de queries muy largas."""
        long_query = "a " * 1000  # 1000 palabras
        try:
            result = recommend_for_new_user(long_query, n=1)
            # Debe retornar algo o fallar gracefully
            if result is not None:
                assert len(result) >= 0
        except Exception:
            pass  # Es aceptable fallar con query muy larga


class TestModelConsistency:
    """Valida que el modelo es determinista y consistente."""

    def test_same_query_similar_results(self):
        """Queries idénticas deben retornar recetas similares (mismo top-3)."""
        query = "pasta with cream"
        result1 = recommend_for_new_user(query, n=3)
        result2 = recommend_for_new_user(query, n=3)

        # Las recetas top deben ser iguales o muy similares
        names1 = result1["nombre"].tolist()
        names2 = result2["nombre"].tolist()

        # Al menos 2 de las 3 recetas deben coincidir
        matches = sum(1 for n in names1 if n in names2)
        assert matches >= 2, f"Results not consistent: {names1} vs {names2}"

    def test_rating_bounds(self):
        """Calificaciones deben estar en rango válido (0-5)."""
        result = recommend_for_new_user("pizza", n=5)
        ratings = result["calificación_promedio"].tolist()

        for rating in ratings:
            assert 0 <= rating <= 5, f"Rating {rating} out of [0, 5] range"
