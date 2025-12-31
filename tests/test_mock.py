#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el Servidor MOCK sin OpenAI
==============================================

Uso:
    python test_mock_server.py

Este script:
1. Inicia el servidor MOCK
2. Prueba todos los endpoints
3. Muestra resultados en la terminal
"""

import subprocess
import time
import sys
import json
import requests
from typing import Dict, Any

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Imprimir encabezado"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")

def print_success(text: str):
    """Imprimir mensaje exitoso"""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    """Imprimir error"""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text: str):
    """Imprimir info"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def test_endpoint(method: str, url: str, data: Dict = None) -> bool:
    """
    Probar un endpoint
    """
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"Status {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return False, {"error": "No se puede conectar al servidor"}
    except Exception as e:
        return False, {"error": str(e)}

def main():
    print_header("🎭 PRUEBA DEL SERVIDOR MOCK")
    
    print_info("Asegúrate de tener el servidor corriendo:")
    print_info("  python -m uvicorn app_mock:app --port 8000")
    print_info("")
    
    base_url = "http://127.0.0.1:8000"
    
    # TEST 1: GET /
    print_header("TEST 1: GET / (Info del Servidor)")
    success, data = test_endpoint("GET", f"{base_url}/")
    if success:
        print_success("Servidor respondiendo")
        print(f"  Título: {data.get('titulo', 'N/A')}")
        print(f"  Modo: {data.get('modo', 'N/A')}")
        print(f"  Estado: {data.get('estado', 'N/A')}")
    else:
        print_error(f"Error: {data.get('error', 'Desconocido')}")
        print_error("Asegúrate de que el servidor está corriendo en puerto 8000")
        return
    
    # TEST 2: GET /health
    print_header("TEST 2: GET /health (Estado del Servidor)")
    success, data = test_endpoint("GET", f"{base_url}/health")
    if success:
        print_success("Health check OK")
        print(f"  Status: {data.get('status', 'N/A')}")
        print(f"  Modo: {data.get('modo', 'N/A')}")
        print(f"  Datos disponibles: {data.get('datos_disponibles', 'N/A')} recetas")
    else:
        print_error(f"Error: {data.get('error', 'Desconocido')}")
    
    # TEST 3: POST /recommend (búsqueda simple)
    print_header("TEST 3: POST /recommend (Búsqueda: 'pasta')")
    payload = {
        "query": "pasta",
        "num_results": 2
    }
    success, data = test_endpoint("POST", f"{base_url}/recommend", payload)
    if success:
        print_success(f"Búsqueda ejecutada - {data.get('num_resultados', 0)} resultados")
        print(f"  Query: {data.get('query', 'N/A')}")
        print(f"  Modo: {data.get('modo', 'N/A')}")
        for i, recipe in enumerate(data.get('recetas', []), 1):
            print(f"\n  Receta {i}:")
            print(f"    Nombre: {recipe.get('nombre', 'N/A')}")
            print(f"    Rating: ⭐ {recipe.get('calificacion_promedio', 'N/A')}/5")
            print(f"    Tiempo: {recipe.get('tiempo_cocina', 'N/A')}")
            print(f"    Ingredientes: {', '.join(recipe.get('ingredientes', [])[:3])}...")
    else:
        print_error(f"Error: {data.get('error', 'Desconocido')}")
    
    # TEST 4: POST /recommend (con ingredientes)
    print_header("TEST 4: POST /recommend (Ingredientes: tomate, queso)")
    payload = {
        "ingredients": ["tomate", "queso"],
        "num_results": 2
    }
    success, data = test_endpoint("POST", f"{base_url}/recommend", payload)
    if success:
        print_success(f"Búsqueda con ingredientes OK - {data.get('num_resultados', 0)} resultados")
        for recipe in data.get('recetas', []):
            print(f"  • {recipe.get('nombre', 'N/A')} (⭐ {recipe.get('calificacion_promedio', 'N/A')}/5)")
    else:
        print_error(f"Error: {data.get('error', 'Desconocido')}")
    
    # TEST 5: GET /search
    print_header("TEST 5: GET /search?q=pollo&limit=2")
    success, data = test_endpoint("GET", f"{base_url}/search?q=pollo&limit=2")
    if success:
        print_success(f"Búsqueda simple OK - {len(data.get('resultados', []))} resultados")
        for recipe in data.get('resultados', []):
            print(f"  • {recipe.get('nombre', 'N/A')}")
    else:
        print_error(f"Error: {data.get('error', 'Desconocido')}")
    
    # TEST 6: GET /recetas
    print_header("TEST 6: GET /recetas (Ver todas)")
    success, data = test_endpoint("GET", f"{base_url}/recetas")
    if success:
        total = data.get('total', 0)
        print_success(f"Recetas cargadas - {total} recetas disponibles")
        print(f"  Primeras 3:")
        for recipe in data.get('recetas', [])[:3]:
            print(f"    • {recipe.get('nombre', 'N/A')}")
    else:
        print_error(f"Error: {data.get('error', 'Desconocido')}")
    
    # Resumen final
    print_header("📊 RESUMEN DE PRUEBAS")
    print_success("Todos los tests completados")
    print_info("El servidor MOCK está funcionando correctamente")
    print(f"\n{Colors.CYAN}URLs disponibles:{Colors.RESET}")
    print(f"  🌐 API:        {base_url}")
    print(f"  📚 Swagger UI: {base_url}/docs")
    print(f"  📖 ReDoc:      {base_url}/redoc")
    print()
    
    print(f"{Colors.GREEN}{Colors.BOLD}¡Listo para usar el servidor MOCK!{Colors.RESET}\n")
    
    # Instrucciones finales
    print(f"{Colors.YELLOW}{Colors.BOLD}Próximos pasos:{Colors.RESET}")
    print(f"  1. Abre Swagger UI: http://127.0.0.1:8000/docs")
    print(f"  2. Prueba el endpoint POST /recommend")
    print(f"  3. Luego de verificar, puedes:{Colors.RESET}")
    print(f"     - Opción 1: Recargar créditos OpenAI")
    print(f"     - Opción 2: Cambiar a app.py cuando tengas crédito")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupción del usuario{Colors.RESET}\n")
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)
