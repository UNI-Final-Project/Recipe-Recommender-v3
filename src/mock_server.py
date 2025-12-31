#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVIDOR CON MODO MOCK - Sin necesidad de OpenAI
================================================

Este archivo contiene funciones para simular respuestas sin llamar a OpenAI.
Útil para testing y desarrollo sin gastar dinero.

Uso:
    USE_MOCK_MODE=true python -m uvicorn app:app --port 8000
"""

import random
from typing import List, Dict, Any

# Mock data de recetas para simular búsquedas
MOCK_RECIPES = [
    {
        "nombre": "Espaguetis Clásicos al Pomodoro",
        "descripción": "Receta italiana tradicional con tomates frescos y ajo",
        "ingredientes": ["espaguetis", "tomates", "ajo", "aceite de oliva", "albahaca"],
        "instrucciones": ["Cocinar espaguetis", "Preparar salsa", "Combinar"],
        "tiempo_cocina": "30 minutos",
        "porciones": 4,
        "calificacion_promedio": 4.8,
        "num_reviews": 1247
    },
    {
        "nombre": "Pasta al Pomodoro con Ajo",
        "descripción": "Deliciosa pasta italiana con salsa de tomate y ajo",
        "ingredientes": ["pasta", "tomates", "ajo", "aceite"],
        "instrucciones": ["Cocinar pasta", "Preparar salsa", "Servir"],
        "tiempo_cocina": "25 minutos",
        "porciones": 4,
        "calificacion_promedio": 4.9,
        "num_reviews": 892
    },
    {
        "nombre": "Pasta Cremosa de Tomate",
        "descripción": "Pasta con salsa cremosa de tomate y queso parmesano",
        "ingredientes": ["pasta", "tomates", "crema", "queso"],
        "instrucciones": ["Cocinar pasta", "Preparar salsa cremosa", "Gratinar"],
        "tiempo_cocina": "35 minutos",
        "porciones": 4,
        "calificacion_promedio": 4.7,
        "num_reviews": 756
    },
    {
        "nombre": "Pollo a la Mostaza",
        "descripción": "Pollo tierno con salsa de mostaza y vino blanco",
        "ingredientes": ["pechuga de pollo", "mostaza", "vino blanco", "cebolla"],
        "instrucciones": ["Cocinar pollo", "Preparar salsa", "Servir"],
        "tiempo_cocina": "40 minutos",
        "porciones": 4,
        "calificacion_promedio": 4.6,
        "num_reviews": 523
    },
    {
        "nombre": "Salmón al Horno",
        "descripción": "Salmón fresco al horno con limón y hierbas aromáticas",
        "ingredientes": ["filete salmón", "limón", "hierbas", "aceite de oliva"],
        "instrucciones": ["Preparar salmón", "Hornear", "Servir"],
        "tiempo_cocina": "20 minutos",
        "porciones": 2,
        "calificacion_promedio": 4.9,
        "num_reviews": 634
    },
    {
        "nombre": "Ensalada Griega",
        "descripción": "Ensalada fresca con queso feta, tomates y aceitunas",
        "ingredientes": ["lechuga", "tomates", "queso feta", "aceitunas", "cebolla"],
        "instrucciones": ["Picar verduras", "Mezclar", "Aliñar"],
        "tiempo_cocina": "10 minutos",
        "porciones": 4,
        "calificacion_promedio": 4.5,
        "num_reviews": 412
    },
    {
        "nombre": "Pizza Casera",
        "descripción": "Pizza casera con masa crujiente y toppings variados",
        "ingredientes": ["harina", "levadura", "tomate", "queso", "jamón"],
        "instrucciones": ["Preparar masa", "Dejar reposar", "Hornear"],
        "tiempo_cocina": "45 minutos",
        "porciones": 4,
        "calificacion_promedio": 4.7,
        "num_reviews": 789
    },
    {
        "nombre": "Sopa de Verduras",
        "descripción": "Sopa caliente con verduras frescas y caldo de pollo",
        "ingredientes": ["caldo", "zanahoria", "papa", "cebolla", "apio"],
        "instrucciones": ["Picar verduras", "Cocinar en caldo", "Servir"],
        "tiempo_cocina": "30 minutos",
        "porciones": 4,
        "calificacion_promedio": 4.4,
        "num_reviews": 345
    },
    {
        "nombre": "Tarta Fría de Chocolate",
        "descripción": "Postre sin horno con chocolate y frutos rojos",
        "ingredientes": ["chocolate", "crema", "galletas", "fresas", "moras"],
        "instrucciones": ["Preparar base", "Hacer relleno", "Refrigerar"],
        "tiempo_cocina": "20 minutos (+ 4h refrigeración)",
        "porciones": 8,
        "calificacion_promedio": 4.8,
        "num_reviews": 567
    },
    {
        "nombre": "Tortilla Española",
        "descripción": "Tortilla con papa y cebolla, receta clásica española",
        "ingredientes": ["huevos", "papa", "cebolla", "aceite", "sal"],
        "instrucciones": ["Freír papa y cebolla", "Mezclar con huevos", "Cuajar"],
        "tiempo_cocina": "25 minutos",
        "porciones": 4,
        "calificacion_promedio": 4.7,
        "num_reviews": 612
    }
]

def get_mock_embedding(text: str) -> List[float]:
    """
    Simula un embedding sin llamar a OpenAI.
    Genera un vector consistente basado en el hash del texto.
    """
    # Crear embedding determinístico basado en el texto
    # (En producción esto sería un vector real de 1536 dimensiones)
    import hashlib
    
    # Usar hash para crear números "pseudo-aleatorios" pero consistentes
    hash_obj = hashlib.md5(text.encode())
    seed = int(hash_obj.hexdigest(), 16)
    
    # Generar 1536 valores normalizados
    random.seed(seed)
    embedding = [random.uniform(-1, 1) for _ in range(1536)]
    
    # Normalizar
    magnitude = sum(x**2 for x in embedding) ** 0.5
    embedding = [x / magnitude for x in embedding]
    
    return embedding

def get_mock_recommendations(query: str, num_results: int = 3) -> List[Dict[str, Any]]:
    """
    Simula la búsqueda de recetas sin llamar a Qdrant.
    Retorna recetas similares de manera simulada.
    """
    
    # Palabras clave asociadas con recetas
    query_lower = query.lower()
    
    # Mapeo de palabras clave a índices de recetas
    keyword_map = {
        "pasta": [0, 1, 2],
        "tomate": [0, 1, 2],
        "pollo": [3],
        "salmón": [4],
        "ensalada": [5],
        "pizza": [6],
        "sopa": [7],
        "chocolate": [8],
        "tortilla": [9],
        "rápida": [0, 1, 4, 5],
        "fácil": [5, 9],
        "vegetariano": [1, 2, 5, 7, 9],
        "vegano": [5, 7],
        "desayuno": [9],
        "cena": [0, 1, 3, 4, 6],
        "postre": [8],
        "limon": [4],
        "hierbas": [4],
        "mostaza": [3],
        "feta": [5],
        "frio": [8],
        "sin horno": [8],
    }
    
    # Encontrar recetas relevantes
    relevant_indices = set()
    
    for keyword, indices in keyword_map.items():
        if keyword in query_lower:
            relevant_indices.update(indices)
    
    # Si no hay matches exactos, retornar recetas aleatorias
    if not relevant_indices:
        relevant_indices = set(random.sample(range(len(MOCK_RECIPES)), min(num_results, len(MOCK_RECIPES))))
    
    # Convertir a lista y seleccionar
    recipe_list = list(relevant_indices)
    random.shuffle(recipe_list)
    selected_indices = recipe_list[:num_results]
    
    # Crear respuesta con scores simulados
    recommendations = []
    for idx in selected_indices:
        recipe = MOCK_RECIPES[idx].copy()
        # Agregar scores simulados
        recipe["relevancia_score"] = round(random.uniform(0.85, 0.99), 3)
        recommendations.append(recipe)
    
    return recommendations

def translate_to_spanish_mock(text: str) -> str:
    """
    Simula traducción a español sin llamar a GPT-4.
    Para este demo, solo retorna el texto original.
    En producción real, esto llamaría a GPT-4.
    """
    # En un modo mock real, podrías usar:
    # - googletrans (library gratuita)
    # - Diccionarios locales
    # - API gratuita de traducción
    
    # Para este demo, simplemente retornamos el texto
    # (asumiendo que ya está en español o inglés está bien)
    return text

def create_mock_response(query: str) -> Dict[str, Any]:
    """
    Crea una respuesta mock completa como lo haría el servidor real.
    """
    
    # Obtener recomendaciones simuladas
    recipes = get_mock_recommendations(query, num_results=3)
    
    return {
        "success": True,
        "query": query,
        "total_results": len(recipes),
        "recetas": recipes,
        "nota": "⚠️ Modo MOCK - Respuestas simuladas sin OpenAI"
    }

# Ejemplo de uso
if __name__ == "__main__":
    # Probar el sistema mock
    test_queries = [
        "pasta",
        "pollo al limón",
        "receta vegetariana",
        "postre de chocolate",
        "desayuno rápido"
    ]
    
    print("\n" + "="*60)
    print("PRUEBA DEL SISTEMA MOCK")
    print("="*60)
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 40)
        
        response = create_mock_response(query)
        
        for i, recipe in enumerate(response["recetas"], 1):
            print(f"\n{i}. {recipe['nombre']}")
            print(f"   Rating: ⭐ {recipe['calificacion_promedio']}/5")
            print(f"   Relevancia: {recipe.get('relevancia_score', 'N/A')}")
            print(f"   Tiempo: {recipe.get('tiempo_cocina', 'N/A')}")
    
    print("\n" + "="*60 + "\n")
