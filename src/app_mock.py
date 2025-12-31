#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVIDOR CON MODO MOCK - Sin OpenAI
====================================

Ejecuta: python app_mock.py
Luego abre: http://127.0.0.1:8000/docs

Este servidor usa respuestas simuladas en lugar de llamar a OpenAI.
Perfecto para testing sin gastar dinero.

Endpoints disponibles:
- GET  /
- GET  /health  
- POST /recommend
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import random
from datetime import datetime

# Importar funciones mock
try:
    try:
        from .mock_server import get_mock_recommendations, create_mock_response
    except ImportError:
        # Fallback para ejecución directa
        from mock_server import get_mock_recommendations, create_mock_response
except ImportError:
    print("⚠️  Error: No se pudo importar mock_server.py")
    print("   Asegúrate de que mock_server.py esté en el mismo directorio")
    sys.exit(1)

# ==================== CONFIGURACIÓN ====================

app = FastAPI(
    title="Recipe Recommender - MODO MOCK",
    description="🎭 Sistema de recomendación sin OpenAI - Respuestas simuladas",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELOS ====================

class RecommendRequest(BaseModel):
    """Solicitud de recomendación"""
    ingredients: Optional[List[str]] = None
    query: Optional[str] = None
    num_results: int = 3
    
    class Config:
        example = {
            "ingredients": ["tomate", "queso"],
            "num_results": 3
        }

class HealthResponse(BaseModel):
    """Respuesta de health check"""
    status: str
    modo: str
    timestamp: str
    datos_disponibles: int

# ==================== ENDPOINTS ====================

@app.get("/", tags=["Info"])
async def root():
    """
    Endpoint raíz - Info del servidor
    """
    return {
        "titulo": "🎭 Recipe Recommender - MODO MOCK",
        "modo": "testing (sin OpenAI)",
        "descripcion": "Sistema de recomendación de recetas con respuestas simuladas",
        "estado": "✅ Operativo",
        "endpoints": {
            "documentación": "http://127.0.0.1:8000/docs",
            "health": "/health",
            "recomendar": "/recommend"
        },
        "nota": "⚠️  Respuestas simuladas - No requiere OpenAI",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"], response_model=HealthResponse)
async def health():
    """
    Health check del servidor
    """
    return HealthResponse(
        status="healthy",
        modo="🎭 MOCK (sin OpenAI)",
        timestamp=datetime.now().isoformat(),
        datos_disponibles=10  # Recetas simuladas disponibles
    )

@app.post("/recommend", tags=["Recomendaciones"])
async def recommend(request: RecommendRequest) -> Dict[str, Any]:
    """
    Obtener recomendaciones de recetas
    
    **Parámetros:**
    - `ingredients`: Lista de ingredientes (ej: ["tomate", "queso"])
    - `query`: Búsqueda por texto libre (ej: "sopa de tomate")
    - `num_results`: Número de resultados (1-10)
    
    **Respuesta:**
    - Recetas recomendadas con puntuación de relevancia
    
    **Ejemplo:**
    ```json
    {
        "ingredients": ["tomate", "queso"],
        "num_results": 3
    }
    ```
    """
    
    try:
        # Validar input
        if not request.query and not request.ingredients:
            return {
                "success": False,
                "error": "Proporciona 'query' o 'ingredients'",
                "ejemplo": {"ingredients": ["tomate"], "num_results": 3}
            }
        
        # Construir query
        if request.query:
            query = request.query
        else:
            query = " ".join(request.ingredients)
        
        # Validar num_results
        if request.num_results < 1 or request.num_results > 10:
            return {
                "success": False,
                "error": "num_results debe estar entre 1 y 10"
            }
        
        # Obtener respuestas mock
        recipes = get_mock_recommendations(query, num_results=request.num_results)
        
        # Construir respuesta
        response = {
            "success": True,
            "modo": "🎭 MOCK (sin OpenAI)",
            "query": query,
            "num_resultados": len(recipes),
            "recetas": recipes,
            "metadata": {
                "tiempo_respuesta_ms": random.randint(10, 50),
                "timestamp": datetime.now().isoformat(),
                "nota": "Respuestas simuladas para testing"
            }
        }
        
        return response
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "modo": "MOCK"
        }

@app.post("/search", tags=["Búsqueda"])
async def search(q: str, limit: int = 5) -> Dict[str, Any]:
    """
    Búsqueda simple de recetas
    
    **Parámetros:**
    - `q`: Término de búsqueda (ej: "pasta")
    - `limit`: Máximo de resultados (1-10)
    """
    
    if not q or len(q) < 2:
        return {
            "success": False,
            "error": "La búsqueda debe tener al menos 2 caracteres"
        }
    
    recipes = get_mock_recommendations(q, num_results=min(limit, 10))
    
    return {
        "success": True,
        "modo": "MOCK",
        "query": q,
        "resultados": recipes
    }

@app.get("/recetas", tags=["Data"])
async def get_recipes_list():
    """
    Listar todas las recetas disponibles
    """
    from mock_server import MOCK_RECIPES
    
    return {
        "success": True,
        "total": len(MOCK_RECIPES),
        "recetas": MOCK_RECIPES
    }

# ==================== MANEJO DE ERRORES ====================

@app.get("/error-test", tags=["Debug"])
async def error_test():
    """
    Endpoint para probar manejo de errores
    """
    raise HTTPException(status_code=500, detail="Error de prueba")

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🎭 SERVIDOR DE RECETAS - MODO MOCK")
    print("="*70)
    print("✅ Sin OpenAI - Respuestas simuladas")
    print("📊 10 recetas disponibles para testing")
    print()
    print("🚀 Iniciando servidor...")
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 Documentación: http://127.0.0.1:8000/docs")
    print("="*70 + "\n")
    
    try:
        uvicorn.run(
            "app_mock:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n❌ Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
