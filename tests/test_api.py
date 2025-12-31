"""
Script para demostrar el flujo completo del sistema MLOps Recipe Recommender
"""
import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 10

def print_section(title):
    """Imprime un encabezado de sección"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_success(msg):
    """Imprime mensaje de éxito"""
    print(f"✅ {msg}")

def print_error(msg):
    """Imprime mensaje de error"""
    print(f"❌ {msg}")

def print_info(msg):
    """Imprime mensaje informativo"""
    print(f"ℹ️  {msg}")

def test_root_endpoint():
    """Prueba el endpoint raíz"""
    print_section("1. Probando Endpoint Raíz (/)")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Conexión exitosa al servidor")
            print(f"Versión API: {data.get('version', 'N/A')}")
            print(f"Endpoints disponibles:")
            for endpoint, path in data.get('endpoints', {}).items():
                print(f"  • {endpoint}: {path}")
            return True
        else:
            print_error(f"Error {response.status_code}")
            return False
    except Exception as e:
        print_error(f"No se pudo conectar: {e}")
        return False

def test_health_endpoint():
    """Prueba el endpoint de health check"""
    print_section("2. Verificando Salud del Sistema (/health)")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success("Sistema saludable")
            print(f"Estado: {data.get('status', 'unknown')}")
            print(f"Recetas cargadas: {data.get('num_recipes', 0):,}")
            print(f"Modelo en producción: {data.get('model_production', 'N/A')}")
            return True
        else:
            print_error(f"Error {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error en health check: {e}")
        return False

def test_models_endpoint():
    """Prueba el endpoint de modelos"""
    print_section("3. Listando Modelos Registrados (/models)")
    try:
        response = requests.get(f"{BASE_URL}/models", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Se encontraron {len(data.get('models', []))} modelo(s)")
            for model in data.get('models', []):
                print(f"\nModelo: {model.get('model_id', 'N/A')}")
                print(f"  Versión: {model.get('version', 'N/A')}")
                print(f"  Estado: {model.get('status', 'N/A')}")
                print(f"  Tipo: {model.get('model_type', 'N/A')}")
            return True
        else:
            print_error(f"Error {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error listando modelos: {e}")
        return False

def test_metrics_endpoint():
    """Prueba el endpoint de métricas"""
    print_section("4. Recolectando Métricas (/metrics)")
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print_success("Métricas obtenidas exitosamente")
            print(f"\nResumen de Métricas:")
            print(f"  Total de peticiones: {data.get('total_requests', 0)}")
            print(f"  Latencia promedio: {data.get('avg_latency_ms', 0):.2f}ms")
            print(f"  Tasa de error: {data.get('error_rate', 0):.2f}%")
            return True
        else:
            print_error(f"Error {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error obteniendo métricas: {e}")
        return False

def test_recommend_endpoint():
    """Prueba el endpoint de recomendaciones"""
    print_section("5. Solicitando Recomendaciones (/recommend)")
    try:
        payload = {
            "query": "delicious pasta with tomato and garlic"
        }
        print_info(f"Consulta: '{payload['query']}'")
        
        response = requests.post(
            f"{BASE_URL}/recommend",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Se obtuvieron {len(data.get('recetas', []))} recomendaciones")
            
            for i, recipe in enumerate(data.get('recetas', [])[:3], 1):
                print(f"\n{i}. {recipe.get('nombre', 'N/A')}")
                print(f"   Calificación: {recipe.get('calificación_promedio', 0):.1f}★")
                print(f"   Descripción: {recipe.get('descripción', 'N/A')[:80]}...")
            return True
        else:
            print_error(f"Error {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print_error(f"Error en recomendación: {e}")
        return False

def test_production_model():
    """Prueba obtener detalles del modelo en producción"""
    print_section("6. Obteniendo Detalles del Modelo de Producción")
    try:
        response = requests.get(
            f"{BASE_URL}/models/hybrid_ranker/production",
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            model = response.json()
            print_success("Modelo de producción obtenido")
            print(f"\nDetalles del Modelo:")
            print(f"  ID: {model.get('model_id', 'N/A')}")
            print(f"  Tipo: {model.get('model_type', 'N/A')}")
            print(f"  Versión: {model.get('version', 'N/A')}")
            print(f"  Estado: {model.get('status', 'N/A')}")
            print(f"  Descripción: {model.get('description', 'N/A')}")
            return True
        else:
            print_error(f"Error {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error obteniendo modelo: {e}")
        return False

def main():
    """Ejecuta el flujo completo"""
    print("\n" + "="*70)
    print("  🚀 FLUJO COMPLETO - RECIPE RECOMMENDER API CON MLOPS")
    print("="*70)
    print(f"\nFecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}\n")
    
    results = []
    
    # Ejecutar todas las pruebas
    results.append(("Endpoint Raíz", test_root_endpoint()))
    time.sleep(1)
    
    results.append(("Health Check", test_health_endpoint()))
    time.sleep(1)
    
    results.append(("Listar Modelos", test_models_endpoint()))
    time.sleep(1)
    
    results.append(("Métricas", test_metrics_endpoint()))
    time.sleep(1)
    
    results.append(("Recomendaciones", test_recommend_endpoint()))
    time.sleep(1)
    
    results.append(("Modelo Producción", test_production_model()))
    
    # Resumen final
    print_section("📊 RESUMEN FINAL")
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    print(f"Pruebas ejecutadas: {total}")
    print(f"Exitosas: {passed} ✅")
    print(f"Fallidas: {failed} ❌")
    print(f"Tasa de éxito: {(passed/total)*100:.1f}%")
    
    print(f"\n{'Prueba':<25} {'Resultado':<20}")
    print("-" * 45)
    for name, result in results:
        status = "✅ PASADA" if result else "❌ FALLIDA"
        print(f"{name:<25} {status:<20}")
    
    print("\n" + "="*70)
    print("  📚 Documentación Interactiva Disponible:")
    print(f"  • Swagger UI: {BASE_URL}/docs")
    print(f"  • ReDoc: {BASE_URL}/redoc")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
