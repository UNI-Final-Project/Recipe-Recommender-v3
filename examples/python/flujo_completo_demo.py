#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEMOSTRACIÓN DEL FLUJO COMPLETO DEL SISTEMA
============================================

Este script simula el flujo completo del sistema Recipe Recommender:
1. Carga de data
2. Generación de embeddings
3. Búsqueda en Qdrant
4. Ranking híbrido
5. Traducción
6. Logging y MLflow

Para ejecutar:
    python flujo_completo_demo.py
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Colores para output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title: str, step: int = None):
    """Imprime un título de sección"""
    if step:
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}PASO {step}: {title}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    else:
        print(f"\n{Colors.CYAN}{Colors.BOLD}>>> {title}{Colors.ENDC}\n")

def print_success(msg: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")

def print_info(msg: str):
    """Imprime información"""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.ENDC}")

def print_warning(msg: str):
    """Imprime advertencia"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")

def print_error(msg: str):
    """Imprime error"""
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")

def simulate_step(description: str, duration: float = 0.5):
    """Simula un paso del proceso con animación"""
    print(f"  {description}...", end="", flush=True)
    time.sleep(duration)
    print(f" {Colors.GREEN}✓{Colors.ENDC}")

# ============================================================================
# PASO 0: INTRODUCCIÓN
# ============================================================================

def intro():
    """Introducción al flujo"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🍽️  DEMOSTRACIÓN: FLUJO COMPLETO DEL SISTEMA  🍽️  ".center(68) + "║")
    print("║" + "  Recipe Recommender con MLOps".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.ENDC}\n")
    
    print(f"{Colors.CYAN}Este script demuestra todos los pasos desde la query del usuario")
    print(f"hasta la respuesta final con recomendaciones.{Colors.ENDC}\n")

# ============================================================================
# PASO 1: USUARIO ENVÍA QUERY
# ============================================================================

def paso1_usuario_query():
    """Simula entrada del usuario"""
    print_section("USUARIO ENVÍA QUERY", 1)
    
    query = "Quiero una deliciosa pasta con tomate y ajo"
    
    print(f"{Colors.YELLOW}Usuario escribe:{Colors.ENDC}")
    print(f"  \"{Colors.BOLD}{query}{Colors.ENDC}\"\n")
    
    print(f"{Colors.BLUE}FastAPI recibe POST request a:{Colors.ENDC}")
    print(f"  POST /recommend")
    print(f"  Content-Type: application/json\n")
    
    print(f"{Colors.BLUE}Body:{Colors.ENDC}")
    body = {"query": query}
    print(f"  {json.dumps(body, indent=2, ensure_ascii=False)}\n")
    
    print_success("Query recibida y validada")
    return query

# ============================================================================
# PASO 2: VALIDACIÓN Y LOGGING
# ============================================================================

def paso2_validacion():
    """Simula validación en FastAPI"""
    print_section("VALIDACIÓN Y LOGGING", 2)
    
    print_info("Validando con Pydantic model")
    simulate_step("Verificando que query no esté vacío", 0.3)
    simulate_step("Verificando que query tenga menos de 1000 caracteres", 0.3)
    
    print(f"\n{Colors.BLUE}Logs creados:{Colors.ENDC}")
    print(f"  logs/app_20251231.json")
    print(f"  {Colors.YELLOW}Event{Colors.ENDC}: recommend_request_received")
    print(f"  {Colors.YELLOW}Timestamp{Colors.ENDC}: 2025-12-31T00:19:18.234")
    
    print_success("Validación completada")
    return True

# ============================================================================
# PASO 3: GENERACIÓN DE EMBEDDINGS
# ============================================================================

def paso3_embeddings():
    """Simula generación de embeddings"""
    print_section("GENERACIÓN DE EMBEDDINGS CON OPENAI", 3)
    
    query = "Quiero una deliciosa pasta con tomate y ajo"
    
    print(f"{Colors.BLUE}API Call:{Colors.ENDC}")
    print(f"  Endpoint: https://api.openai.com/v1/embeddings")
    print(f"  Model: text-embedding-3-small")
    print(f"  Input: \"{query}\"\n")
    
    simulate_step("Enviando request a OpenAI", 0.4)
    simulate_step("Esperando respuesta", 0.6)
    
    print(f"\n{Colors.BLUE}Respuesta:{Colors.ENDC}")
    print(f"  Dimensions: 1536")
    print(f"  Vector: [0.0234, -0.0156, 0.0412, ..., -0.0078]")
    print(f"  Tokens usados: 8\n")
    
    print_success("Embedding generado exitosamente")
    print_info("Tiempo total: ~250ms")
    
    return [0.0234, -0.0156, 0.0412, -0.0078]  # Simulación

# ============================================================================
# PASO 4: BÚSQUEDA EN QDRANT
# ============================================================================

def paso4_qdrant_search():
    """Simula búsqueda en Qdrant"""
    print_section("BÚSQUEDA SEMÁNTICA EN QDRANT", 4)
    
    print(f"{Colors.BLUE}Base de datos:{Colors.ENDC}")
    print(f"  Qdrant Cloud")
    print(f"  Collection: recipes")
    print(f"  Total vectores: 53,064\n")
    
    simulate_step("Conectando a Qdrant", 0.3)
    simulate_step("Calculando similitud con todos los vectores", 0.8)
    simulate_step("Ordenando resultados", 0.2)
    
    print(f"\n{Colors.BLUE}Top 6 resultados encontrados:{Colors.ENDC}\n")
    
    results = [
        {"rank": 1, "name": "Classic Spaghetti al Pomodoro", "score": 0.952, "rating": 4.8},
        {"rank": 2, "name": "Pasta al Pomodoro con Ajo", "score": 0.941, "rating": 4.9},
        {"rank": 3, "name": "Creamy Tomato Pasta", "score": 0.925, "rating": 4.7},
        {"rank": 4, "name": "Spaghetti Aglio e Olio", "score": 0.891, "rating": 4.6},
        {"rank": 5, "name": "Garlic Tomato Fettuccine", "score": 0.878, "rating": 4.5},
        {"rank": 6, "name": "Pasta Marinara", "score": 0.865, "rating": 4.4},
    ]
    
    for r in results:
        print(f"  {r['rank']}. {r['name']}")
        print(f"     Semantic Score: {r['score']:.3f} | Rating: ⭐ {r['rating']}/5")
    
    print_success("Búsqueda completada en Qdrant")
    print_info("Tiempo total: ~150ms")
    
    return results

# ============================================================================
# PASO 5: RANKING HÍBRIDO
# ============================================================================

def paso5_hybrid_ranking(results: List[Dict]):
    """Simula ranking híbrido"""
    print_section("RANKING HÍBRIDO (70% semántico + 30% popularidad)", 5)
    
    print(f"{Colors.BLUE}Fórmula:{Colors.ENDC}")
    print(f"  Hybrid Score = (α × Semantic) + ((1-α) × Popularity)")
    print(f"  Donde α = 0.7\n")
    
    simulate_step("Normalizando scores de popularidad", 0.3)
    simulate_step("Calculando hybrid score para cada receta", 0.4)
    simulate_step("Reordenando por score final", 0.2)
    
    print(f"\n{Colors.BLUE}Top 3 después de ranking híbrido:{Colors.ENDC}\n")
    
    ranked = [
        {
            "rank": 1,
            "name": "Classic Spaghetti al Pomodoro",
            "semantic": 0.952,
            "popularity": 0.96,
            "hybrid": (0.7 * 0.952) + (0.3 * 0.96)
        },
        {
            "rank": 2,
            "name": "Pasta al Pomodoro con Ajo",
            "semantic": 0.941,
            "popularity": 0.98,
            "hybrid": (0.7 * 0.941) + (0.3 * 0.98)
        },
        {
            "rank": 3,
            "name": "Creamy Tomato Pasta",
            "semantic": 0.925,
            "popularity": 0.94,
            "hybrid": (0.7 * 0.925) + (0.3 * 0.94)
        },
    ]
    
    for r in ranked:
        print(f"  {r['rank']}. {r['name']}")
        print(f"     Semantic: {r['semantic']:.3f} × 0.7 = {r['semantic'] * 0.7:.3f}")
        print(f"     Popularity: {r['popularity']:.3f} × 0.3 = {r['popularity'] * 0.3:.3f}")
        print(f"     {Colors.BOLD}Hybrid Score: {r['hybrid']:.3f}{Colors.ENDC}")
        print()
    
    print_success("Ranking híbrido completado")
    return ranked

# ============================================================================
# PASO 6: EXTRACCIÓN DE DATOS
# ============================================================================

def paso6_extract_data():
    """Simula extracción de datos"""
    print_section("EXTRACCIÓN DE DATOS COMPLETOS", 6)
    
    print(f"{Colors.BLUE}Para cada una de las 3 mejores recetas:{Colors.ENDC}\n")
    
    simulate_step("Buscando receta #1 en food.pkl", 0.2)
    simulate_step("Buscando receta #2 en food.pkl", 0.2)
    simulate_step("Buscando receta #3 en food.pkl", 0.2)
    
    print(f"\n{Colors.BLUE}Datos extraídos para: Classic Spaghetti al Pomodoro{Colors.ENDC}\n")
    
    recipe = {
        "nombre": "Classic Spaghetti al Pomodoro",
        "descripción": "Traditional Italian pasta recipe with fresh tomatoes and garlic",
        "ingredientes": ["spaghetti", "tomatoes", "garlic", "olive oil", "basil"],
        "instrucciones": [
            "Cook spaghetti according to package directions",
            "Prepare tomato sauce with garlic",
            "Combine pasta and sauce",
            "Garnish with fresh basil"
        ],
        "tiempo_cocina": "30 minutos",
        "porciones": 4,
        "calificacion_promedio": 4.8,
        "num_reviews": 1247
    }
    
    print(json.dumps(recipe, indent=2, ensure_ascii=False))
    
    print_success("Datos extraídos exitosamente")
    print_info("Tiempo total: ~80ms")
    
    return recipe

# ============================================================================
# PASO 7: MONITOREO Y MÉTRICAS
# ============================================================================

def paso7_monitoring():
    """Simula recolección de métricas"""
    print_section("MONITOREO Y RECOLECCIÓN DE MÉTRICAS", 7)
    
    print(f"{Colors.BLUE}Métricas recolectadas:{Colors.ENDC}\n")
    
    metrics = {
        "endpoint": "/recommend",
        "method": "POST",
        "status": 200,
        "latency_ms": 245,
        "timestamp": "2025-12-31T00:19:18.234Z",
        "user_id": "anonymous",
        "query_length": 43,
        "num_results": 3
    }
    
    for key, value in metrics.items():
        print(f"  {Colors.YELLOW}{key}{Colors.ENDC}: {value}")
    
    print(f"\n{Colors.BLUE}Anomaly Detection:{Colors.ENDC}")
    print(f"  Latencia > 500ms? {Colors.GREEN}No ✓{Colors.ENDC}")
    print(f"  Error rate > 5%? {Colors.GREEN}No ✓{Colors.ENDC}")
    print(f"  Spike en tráfico? {Colors.GREEN}No ✓{Colors.ENDC}")
    
    print_success("Métricas recolectadas sin anomalías")
    
    return metrics

# ============================================================================
# PASO 8: MLFLOW TRACKING
# ============================================================================

def paso8_mlflow():
    """Simula tracking en MLflow"""
    print_section("TRACKING EN MLFLOW", 8)
    
    print(f"{Colors.BLUE}MLflow Experiment:{Colors.ENDC}")
    print(f"  Name: recipe-recommendations")
    print(f"  ID: 0")
    print(f"  Creation time: 2025-12-31 00:00:00\n")
    
    simulate_step("Iniciando run en MLflow", 0.2)
    simulate_step("Registrando parámetros", 0.2)
    simulate_step("Registrando métricas", 0.2)
    simulate_step("Guardando artefactos", 0.1)
    simulate_step("Finalizando run", 0.1)
    
    print(f"\n{Colors.BLUE}Run Information:{Colors.ENDC}")
    print(f"  Run ID: abc123def456")
    print(f"  Status: FINISHED")
    print(f"  Duration: 245ms\n")
    
    print(f"{Colors.BLUE}Parámetros registrados:{Colors.ENDC}")
    print(f"  embedding_model: text-embedding-3-small")
    print(f"  alpha: 0.7")
    print(f"  n_results: 3\n")
    
    print(f"{Colors.BLUE}Métricas registradas:{Colors.ENDC}")
    print(f"  latency_ms: 245")
    print(f"  semantic_score: 0.952")
    print(f"  hybrid_score: 0.947\n")
    
    print_success("MLflow tracking completado")
    print_info("Artifacts guardados en: ./mlruns/0/abc123def456")

# ============================================================================
# PASO 9: TRADUCCIÓN CON GPT-4
# ============================================================================

def paso9_translation():
    """Simula traducción con GPT-4"""
    print_section("TRADUCCIÓN AL ESPAÑOL CON GPT-4", 9)
    
    print(f"{Colors.BLUE}Enviando contenido a GPT-4 para traducción{Colors.ENDC}\n")
    
    simulate_step("Conectando a OpenAI API", 0.3)
    simulate_step("Enviando prompt de traducción", 0.4)
    simulate_step("Procesando en GPT-4", 0.8)
    
    print(f"\n{Colors.BLUE}Antes (English):{Colors.ENDC}")
    print(f"  \"Classic Spaghetti al Pomodoro - Traditional Italian pasta recipe\"")
    print(f"  \"with fresh tomatoes and garlic. Perfect for a family dinner.\"\n")
    
    print(f"{Colors.BLUE}Después (Spanish):{Colors.ENDC}")
    print(f"  \"Espaguetis Clásicos al Pomodoro - Receta de pasta italiana tradicional\"")
    print(f"  \"con tomates frescos y ajo. Perfecta para la cena familiar.\"\n")
    
    print_success("Traducción completada")
    print_info("Tiempo total: ~800ms")

# ============================================================================
# PASO 10: RESPUESTA AL USUARIO
# ============================================================================

def paso10_response():
    """Simula respuesta final"""
    print_section("RESPUESTA ENVIADA AL USUARIO", 10)
    
    print(f"{Colors.BLUE}HTTP Response:{Colors.ENDC}")
    print(f"  Status: 200 OK")
    print(f"  Content-Type: application/json")
    print(f"  Response Time: 245ms\n")
    
    print(f"{Colors.BLUE}Response Body:{Colors.ENDC}\n")
    
    response = {
        "success": True,
        "query": "Quiero una deliciosa pasta con tomate y ajo",
        "total_results": 3,
        "recetas": [
            {
                "id": 1,
                "nombre": "Espaguetis Clásicos al Pomodoro",
                "descripción": "Receta de pasta italiana tradicional con tomates frescos y ajo",
                "ingredientes": ["espaguetis", "tomates", "ajo", "aceite de oliva", "albahaca"],
                "instrucciones": [
                    "Cocinar los espaguetis según las instrucciones del empaque",
                    "Preparar la salsa de tomate con ajo",
                    "Combinar la pasta con la salsa",
                    "Adornar con albahaca fresca"
                ],
                "tiempo_cocina": "30 minutos",
                "porciones": 4,
                "calificacion_promedio": 4.8,
                "relevancia_score": 0.947
            },
            {
                "id": 2,
                "nombre": "Pasta al Pomodoro con Ajo",
                "descripción": "Deliciosa pasta italiana con salsa de tomate y ajo",
                "calificacion_promedio": 4.9,
                "relevancia_score": 0.939
            },
            {
                "id": 3,
                "nombre": "Pasta Cremosa de Tomate",
                "descripción": "Pasta con salsa cremosa de tomate",
                "calificacion_promedio": 4.7,
                "relevancia_score": 0.925
            }
        ]
    }
    
    print(json.dumps(response, indent=2, ensure_ascii=False)[:1000] + "...")
    
    print(f"\n{Colors.GREEN}✨ RESPUESTA ENVIADA AL USUARIO ✨{Colors.ENDC}")

# ============================================================================
# PASO 11: LOGGING FINAL Y AUDITORÍA
# ============================================================================

def paso11_logging():
    """Simula logging final"""
    print_section("LOGGING FINAL Y AUDITORÍA", 11)
    
    print(f"{Colors.BLUE}Logs guardados en: logs/app_20251231.json{Colors.ENDC}\n")
    
    log_entry = {
        "timestamp": "2025-12-31T00:19:18.234Z",
        "level": "INFO",
        "logger": "app",
        "event": "recommend_completed",
        "endpoint": "/recommend",
        "method": "POST",
        "status_code": 200,
        "latency_ms": 245,
        "query_length": 43,
        "num_results": 3,
        "model_version": "1.0.0",
        "success": True
    }
    
    print(json.dumps(log_entry, indent=2))
    
    print(f"\n{Colors.BLUE}Logs guardados en: logs/mlops_20251231.json{Colors.ENDC}\n")
    
    mlops_entry = {
        "timestamp": "2025-12-31T00:19:18.234Z",
        "level": "INFO",
        "logger": "mlops",
        "event": "recommendation_logged",
        "model_name": "hybrid_ranker",
        "model_version": "1.0.0",
        "embedding_model": "text-embedding-3-small",
        "alpha": 0.7,
        "semantic_score": 0.952,
        "hybrid_score": 0.947
    }
    
    print(json.dumps(mlops_entry, indent=2))
    
    print_success("Todos los logs registrados exitosamente")

# ============================================================================
# RESUMEN FINAL
# ============================================================================

def resumen_final():
    """Muestra resumen final"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  ✅ FLUJO COMPLETO FINALIZADO EXITOSAMENTE  ✅  ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    print(f"{Colors.ENDC}\n")
    
    print(f"{Colors.GREEN}{Colors.BOLD}ESTADÍSTICAS FINALES:{Colors.ENDC}\n")
    
    stats = {
        "Total steps": 11,
        "Total time": "~245ms",
        "Requests processed": 1,
        "Recipes recommended": 3,
        "API calls": 3,  # OpenAI embedding, Qdrant search, GPT-4 translation
        "Logs created": 2,
        "MLflow runs": 1,
        "Success rate": "100%"
    }
    
    for key, value in stats.items():
        print(f"  {Colors.YELLOW}{key}{Colors.ENDC}: {Colors.CYAN}{value}{Colors.ENDC}")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}COMPONENTES ACTIVOS:{Colors.ENDC}\n")
    
    components = [
        ("FastAPI", "Puerto 8000", "✅"),
        ("Qdrant", "Cloud Database", "✅"),
        ("OpenAI", "Embeddings + GPT-4", "✅"),
        ("MLflow", "./mlruns", "✅"),
        ("Logging", "logs/ (JSON)", "✅"),
        ("Monitoring", "Real-time metrics", "✅"),
    ]
    
    for comp, detail, status in components:
        print(f"  {status} {Colors.YELLOW}{comp}{Colors.ENDC} - {detail}")
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}PRÓXIMOS PASOS:{Colors.ENDC}\n")
    print(f"  1. Inicia el servidor:")
    print(f"     {Colors.YELLOW}python -m uvicorn app:app --port 8000{Colors.ENDC}\n")
    print(f"  2. Accede a Swagger UI:")
    print(f"     {Colors.YELLOW}http://127.0.0.1:8000/docs{Colors.ENDC}\n")
    print(f"  3. Prueba los endpoints disponibles:")
    print(f"     {Colors.YELLOW}/recommend{Colors.ENDC} - Obtener recomendaciones")
    print(f"     {Colors.YELLOW}/health{Colors.ENDC} - Estado del sistema")
    print(f"     {Colors.YELLOW}/metrics{Colors.ENDC} - Métricas en tiempo real")
    print(f"     {Colors.YELLOW}/models{Colors.ENDC} - Modelos disponibles")
    print(f"     {Colors.YELLOW}/retrain/check{Colors.ENDC} - Verificar reentrenamiento\n")
    
    print(f"{Colors.GREEN}{Colors.BOLD}¡EL SISTEMA ESTÁ LISTO PARA PRODUCCIÓN! 🚀{Colors.ENDC}\n")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal"""
    intro()
    
    # Paso 1
    query = paso1_usuario_query()
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Paso 2
    paso2_validacion()
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Paso 3
    paso3_embeddings()
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Paso 4
    results = paso4_qdrant_search()
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Paso 5
    ranked = paso5_hybrid_ranking(results)
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Paso 6
    paso6_extract_data()
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Paso 7
    paso7_monitoring()
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Paso 8
    paso8_mlflow()
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Paso 9
    paso9_translation()
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Paso 10
    paso10_response()
    input(f"\n{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Paso 11
    paso11_logging()
    input(f"\n{Colors.CYAN}Presiona Enter para ver resumen...{Colors.ENDC}")
    
    # Resumen
    resumen_final()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}\n⚠️  Ejecución cancelada por el usuario{Colors.ENDC}\n")
        sys.exit(0)
