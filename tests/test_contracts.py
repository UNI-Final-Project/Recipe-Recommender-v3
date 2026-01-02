"""
Test de Contrato: Valida que RecommendResponse y QueryIn cumplen con Pydantic schemas.
Garantiza compatibilidad de API hacia el frontend.
"""

import pytest
from pydantic import ValidationError
from app import RecommendResponse, QueryIn, RecipeOut


class TestQueryInSchema:
    """Valida el schema de entrada QueryIn."""

    def test_valid_query(self):
        """Acepta query válida."""
        q = QueryIn(query="tomato soup")
        assert q.query == "tomato soup"

    def test_empty_query_fails(self):
        """Rechaza query vacía."""
        with pytest.raises(ValidationError):
            QueryIn(query="")

    def test_query_type_validation(self):
        """Rechaza tipos no-string."""
        with pytest.raises(ValidationError):
            QueryIn(query=123)  # type: ignore


class TestRecipeOutSchema:
    """Valida el schema de salida RecipeOut."""

    def test_valid_recipe(self):
        """Acepta receta con todos los campos."""
        recipe = RecipeOut(
            nombre="Pasta Carbonara",
            descripción="Delicious Italian pasta",
            ingredientes=["pasta", "huevos", "queso"],
            instrucciones=["Hervir pasta", "Mezclar huevos"],
            calificación_promedio=4.5,
        )
        assert recipe.nombre == "Pasta Carbonara"
        assert len(recipe.ingredientes) == 3

    def test_parse_ingredientes_string_to_list(self):
        """Convierte string de ingredientes a lista."""
        recipe = RecipeOut(
            nombre="Pizza",
            descripción="Italian pizza",
            ingredientes="['harina', 'queso', 'tomate']",  # String format
            instrucciones=["mezclar", "hornear"],
            calificación_promedio=4.0,
        )
        assert isinstance(recipe.ingredientes, list)
        assert len(recipe.ingredientes) == 3

    def test_parse_instrucciones_string_to_list(self):
        """Convierte string de instrucciones a lista."""
        recipe = RecipeOut(
            nombre="Soup",
            descripción="Vegetable soup",
            ingredientes=["water", "vegetables"],
            instrucciones="['boil water', 'add vegetables', 'simmer']",  # String format
            calificación_promedio=3.8,
        )
        assert isinstance(recipe.instrucciones, list)
        assert len(recipe.instrucciones) == 3

    def test_invalid_rating_range(self):
        """Calificación debe ser numérica (aunque no hay validación de rango en Pydantic)."""
        recipe = RecipeOut(
            nombre="Dish",
            descripción="Test",
            ingredientes=["a"],
            instrucciones=["b"],
            calificación_promedio=10.5,  # Permitido por schema
        )
        assert recipe.calificación_promedio == 10.5

    def test_missing_required_field_fails(self):
        """Rechaza si falta campo requerido."""
        with pytest.raises(ValidationError):
            RecipeOut(
                nombre="Pizza",
                descripción="Pizza",
                ingredientes=["queso"],
                # Falta instrucciones
                calificación_promedio=4.0,  # type: ignore
            )


class TestRecommendResponseSchema:
    """Valida el schema de respuesta RecommendResponse."""

    def test_valid_response(self):
        """Acepta respuesta con lista de recetas."""
        response = RecommendResponse(
            recetas=[
                RecipeOut(
                    nombre="Pasta",
                    descripción="Pasta dish",
                    ingredientes=["pasta"],
                    instrucciones=["cook"],
                    calificación_promedio=4.5,
                )
            ]
        )
        assert len(response.recetas) == 1
        assert response.recetas[0].nombre == "Pasta"

    def test_empty_recipes_list(self):
        """Acepta lista vacía (edge case)."""
        response = RecommendResponse(recetas=[])
        assert len(response.recetas) == 0

    def test_multiple_recipes(self):
        """Acepta múltiples recetas."""
        recipes = [
            RecipeOut(
                nombre=f"Recipe {i}",
                descripción=f"Description {i}",
                ingredientes=["a"],
                instrucciones=["b"],
                calificación_promedio=4.0,
            )
            for i in range(5)
        ]
        response = RecommendResponse(recetas=recipes)
        assert len(response.recetas) == 5

    def test_json_serialization(self):
        """Respuesta es serializable a JSON (para FastAPI)."""
        response = RecommendResponse(
            recetas=[
                RecipeOut(
                    nombre="Test",
                    descripción="Test desc",
                    ingredientes=["a"],
                    instrucciones=["b"],
                    calificación_promedio=4.0,
                )
            ]
        )
        json_str = response.json()
        assert "Test" in json_str
        assert "ingredientes" in json_str
