#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EJEMPLOS PRÁCTICOS DE BÚSQUEDAS EN EL SERVIDOR
==============================================

Ejemplos reales de cómo usar cada endpoint del servidor Recipe Recommender
con diferentes queries, filtros y casos de uso.

Ejecutar el servidor primero:
    python -m uvicorn app:app --port 8000

Luego ejecutar este script:
    python ejemplos_busquedas.py
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime

# URL base del servidor
BASE_URL = "http://127.0.0.1:8000"

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

def print_header(title: str):
    """Imprime encabezado de sección"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_request(method: str, endpoint: str, body: Dict = None):
    """Imprime detalles del request"""
    print(f"{Colors.BLUE}{Colors.BOLD}REQUEST:{Colors.ENDC}")
    print(f"  {Colors.YELLOW}{method} {endpoint}{Colors.ENDC}")
    if body:
        print(f"  Body: {json.dumps(body, indent=4, ensure_ascii=False)}")
    print()

def print_response(response: requests.Response):
    """Imprime respuesta"""
    status_color = Colors.GREEN if response.status_code == 200 else Colors.RED
    print(f"{Colors.BLUE}{Colors.BOLD}RESPONSE:{Colors.ENDC}")
    print(f"  Status: {status_color}{response.status_code}{Colors.ENDC}")
    try:
        data = response.json()
        print(f"  Body:")
        print(f"    {json.dumps(data, indent=4, ensure_ascii=False)}")
    except:
        print(f"  Body: {response.text}")
    print()

def test_health():
    """Verifica que el servidor está corriendo"""
    print_header("1️⃣  VERIFICAR SALUD DEL SERVIDOR")
    print(f"{Colors.CYAN}¿Está el servidor activo?{Colors.ENDC}\n")
    
    print_request("GET", "/health")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print_response(response)
        
        if response.status_code == 200:
            print(f"{Colors.GREEN}✅ Servidor está funcionando correctamente{Colors.ENDC}\n")
            return True
        else:
            print(f"{Colors.RED}❌ Servidor respondió con error{Colors.ENDC}\n")
            return False
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ No se puede conectar al servidor{Colors.ENDC}")
        print(f"{Colors.YELLOW}Asegúrate de que está corriendo:{Colors.ENDC}")
        print(f"  python -m uvicorn app:app --port 8000\n")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.ENDC}\n")
        return False

# ============================================================================
# EJEMPLOS DE BÚSQUEDAS - /recommend
# ============================================================================

def ejemplo_busqueda_simple():
    """Búsqueda simple con una palabra clave"""
    print_header("2️⃣  BÚSQUEDA SIMPLE: Una palabra")
    print(f"{Colors.CYAN}Buscar recetas con pasta{Colors.ENDC}\n")
    
    query = "pasta"
    body = {"query": query}
    
    print_request("POST", "/recommend", body)
    
    response = requests.post(f"{BASE_URL}/recommend", json=body)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"{Colors.GREEN}✅ Se encontraron {len(data.get('recetas', []))} recetas{Colors.ENDC}\n")

def ejemplo_busqueda_compleja():
    """Búsqueda con frase completa"""
    print_header("3️⃣  BÚSQUEDA COMPLEJA: Frase completa")
    print(f"{Colors.CYAN}Buscar: 'Quiero una deliciosa pasta con tomate y ajo'{Colors.ENDC}\n")
    
    query = "Quiero una deliciosa pasta con tomate y ajo"
    body = {"query": query}
    
    print_request("POST", "/recommend", body)
    
    response = requests.post(f"{BASE_URL}/recommend", json=body)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"{Colors.GREEN}✅ Se encontraron {len(data.get('recetas', []))} recetas{Colors.ENDC}\n")

def ejemplo_busqueda_español():
    """Búsqueda en español"""
    print_header("4️⃣  BÚSQUEDA EN ESPAÑOL")
    print(f"{Colors.CYAN}Buscar: 'Comida sana con pollo y verduras'{Colors.ENDC}\n")
    
    query = "Comida sana con pollo y verduras"
    body = {"query": query}
    
    print_request("POST", "/recommend", body)
    
    response = requests.post(f"{BASE_URL}/recommend", json=body)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        recetas = data.get('recetas', [])
        print(f"{Colors.GREEN}✅ Se encontraron {len(recetas)} recetas en español{Colors.ENDC}\n")
        if recetas:
            print(f"{Colors.CYAN}Primera receta:{Colors.ENDC}")
            print(f"  Nombre: {recetas[0].get('nombre', 'N/A')}")
            print(f"  Descripción: {recetas[0].get('descripción', 'N/A')[:100]}...\n")

def ejemplo_busqueda_dieta():
    """Búsqueda por tipo de dieta"""
    print_header("5️⃣  BÚSQUEDA POR DIETA: Vegetariano")
    print(f"{Colors.CYAN}Buscar: 'Recetas vegetarianas rápidas'{Colors.ENDC}\n")
    
    query = "Recetas vegetarianas rápidas"
    body = {"query": query}
    
    print_request("POST", "/recommend", body)
    
    response = requests.post(f"{BASE_URL}/recommend", json=body)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"{Colors.GREEN}✅ Se encontraron {len(data.get('recetas', []))} recetas vegetarianas{Colors.ENDC}\n")

def ejemplo_busqueda_tiempo():
    """Búsqueda por tiempo de preparación"""
    print_header("6️⃣  BÚSQUEDA POR TIEMPO: Rápida")
    print(f"{Colors.CYAN}Buscar: 'Receta rápida para cenar en 15 minutos'{Colors.ENDC}\n")
    
    query = "Receta rápida para cenar en 15 minutos"
    body = {"query": query}
    
    print_request("POST", "/recommend", body)
    
    response = requests.post(f"{BASE_URL}/recommend", json=body)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"{Colors.GREEN}✅ Se encontraron {len(data.get('recetas', []))} recetas rápidas{Colors.ENDC}\n")

def ejemplo_busqueda_ingredientes():
    """Búsqueda por ingredientes específicos"""
    print_header("7️⃣  BÚSQUEDA POR INGREDIENTES")
    print(f"{Colors.CYAN}Buscar: 'Receta con salmón, limón y aceite de oliva'{Colors.ENDC}\n")
    
    query = "Receta con salmón, limón y aceite de oliva"
    body = {"query": query}
    
    print_request("POST", "/recommend", body)
    
    response = requests.post(f"{BASE_URL}/recommend", json=body)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"{Colors.GREEN}✅ Se encontraron {len(data.get('recetas', []))} recetas{Colors.ENDC}\n")

def ejemplo_busqueda_cuisina():
    """Búsqueda por tipo de cocina"""
    print_header("8️⃣  BÚSQUEDA POR COCINA: Italiana")
    print(f"{Colors.CYAN}Buscar: 'Recetas italianas auténticas'{Colors.ENDC}\n")
    
    query = "Recetas italianas auténticas"
    body = {"query": query}
    
    print_request("POST", "/recommend", body)
    
    response = requests.post(f"{BASE_URL}/recommend", json=body)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"{Colors.GREEN}✅ Se encontraron {len(data.get('recetas', []))} recetas italianas{Colors.ENDC}\n")

def ejemplo_busqueda_nivel():
    """Búsqueda por nivel de dificultad"""
    print_header("9️⃣  BÚSQUEDA POR DIFICULTAD: Fácil")
    print(f"{Colors.CYAN}Buscar: 'Receta fácil para principiantes'{Colors.ENDC}\n")
    
    query = "Receta fácil para principiantes"
    body = {"query": query}
    
    print_request("POST", "/recommend", body)
    
    response = requests.post(f"{BASE_URL}/recommend", json=body)
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"{Colors.GREEN}✅ Se encontraron {len(data.get('recetas', []))} recetas fáciles{Colors.ENDC}\n")

# ============================================================================
# OTROS ENDPOINTS
# ============================================================================

def ejemplo_info_sistema():
    """Información del sistema"""
    print_header("🔟 INFORMACIÓN DEL SISTEMA")
    print(f"{Colors.CYAN}¿Qué información expone el sistema?{Colors.ENDC}\n")
    
    print_request("GET", "/")
    
    response = requests.get(f"{BASE_URL}/")
    print_response(response)

def ejemplo_metricas():
    """Métricas del sistema"""
    print_header("1️⃣1️⃣ MÉTRICAS EN TIEMPO REAL")
    print(f"{Colors.CYAN}¿Cómo está performando el sistema?{Colors.ENDC}\n")
    
    print_request("GET", "/metrics")
    
    response = requests.get(f"{BASE_URL}/metrics")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        metrics = data.get('metrics', {})
        print(f"{Colors.CYAN}Métricas principales:{Colors.ENDC}")
        print(f"  Total requests: {metrics.get('total_requests', 'N/A')}")
        print(f"  Promedio latencia: {metrics.get('avg_latency_ms', 'N/A')}ms")
        print(f"  Error rate: {metrics.get('error_rate', 'N/A')}%\n")

def ejemplo_modelos():
    """Modelos disponibles"""
    print_header("1️⃣2️⃣ MODELOS DISPONIBLES")
    print(f"{Colors.CYAN}¿Qué modelos están registrados?{Colors.ENDC}\n")
    
    print_request("GET", "/models")
    
    response = requests.get(f"{BASE_URL}/models")
    print_response(response)

def ejemplo_verificar_reentrenamiento():
    """Verificar si necesita reentrenamiento"""
    print_header("1️⃣3️⃣ VERIFICAR REENTRENAMIENTO")
    print(f"{Colors.CYAN}¿El modelo necesita reentrenamiento?{Colors.ENDC}\n")
    
    print_request("POST", "/retrain/check")
    
    response = requests.post(f"{BASE_URL}/retrain/check")
    print_response(response)

# ============================================================================
# EJEMPLOS CON CURL
# ============================================================================

def mostrar_ejemplos_curl():
    """Muestra ejemplos con comando curl"""
    print_header("📝 EJEMPLOS CON CURL (Terminal)")
    
    ejemplos = [
        {
            "titulo": "Búsqueda simple con CURL",
            "comando": 'curl -X POST "http://127.0.0.1:8000/recommend" -H "Content-Type: application/json" -d "{\\"query\\":\\"pasta\\"}"'
        },
        {
            "titulo": "Búsqueda compleja con CURL",
            "comando": 'curl -X POST "http://127.0.0.1:8000/recommend" -H "Content-Type: application/json" -d "{\\"query\\":\\"receta con pollo y limón\\"}"'
        },
        {
            "titulo": "Verificar salud con CURL",
            "comando": 'curl "http://127.0.0.1:8000/health"'
        },
        {
            "titulo": "Ver métricas con CURL",
            "comando": 'curl "http://127.0.0.1:8000/metrics"'
        },
        {
            "titulo": "Ver modelos con CURL",
            "comando": 'curl "http://127.0.0.1:8000/models"'
        },
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"{Colors.YELLOW}{i}. {ejemplo['titulo']}{Colors.ENDC}")
        print(f"{Colors.CYAN}{ejemplo['comando']}{Colors.ENDC}\n")

# ============================================================================
# EJEMPLOS CON PYTHON REQUESTS
# ============================================================================

def mostrar_ejemplos_python():
    """Muestra ejemplos con Python requests"""
    print_header("🐍 EJEMPLOS CON PYTHON REQUESTS")
    
    ejemplos = [
        {
            "titulo": "Búsqueda simple",
            "codigo": '''
import requests

response = requests.post(
    "http://127.0.0.1:8000/recommend",
    json={"query": "pasta"}
)

print(response.json())
'''
        },
        {
            "titulo": "Búsqueda con frase completa",
            "codigo": '''
import requests

query = "Receta saludable con verduras"
response = requests.post(
    "http://127.0.0.1:8000/recommend",
    json={"query": query}
)

recetas = response.json()["recetas"]
for receta in recetas:
    print(f"- {receta['nombre']}")
'''
        },
        {
            "titulo": "Ver métricas",
            "codigo": '''
import requests

response = requests.get("http://127.0.0.1:8000/metrics")
metrics = response.json()

print(f"Total requests: {metrics['metrics']['total_requests']}")
print(f"Avg latencia: {metrics['metrics']['avg_latency_ms']}ms")
'''
        },
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"{Colors.YELLOW}{i}. {ejemplo['titulo']}{Colors.ENDC}")
        print(f"{Colors.CYAN}{ejemplo['codigo']}{Colors.ENDC}\n")

# ============================================================================
# EJEMPLOS CON POWERSHELL
# ============================================================================

def mostrar_ejemplos_powershell():
    """Muestra ejemplos con PowerShell"""
    print_header("🔵 EJEMPLOS CON POWERSHELL")
    
    ejemplos = [
        {
            "titulo": "Búsqueda simple",
            "comando": '''$body = @{query="pasta"} | ConvertTo-Json
Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommend" -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json'''
        },
        {
            "titulo": "Ver métricas",
            "comando": 'Invoke-WebRequest -Uri "http://127.0.0.1:8000/metrics" | ConvertTo-Json'
        },
        {
            "titulo": "Verificar salud",
            "comando": 'Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" | Select-Object -ExpandProperty Content | ConvertFrom-Json'
        },
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"{Colors.YELLOW}{i}. {ejemplo['titulo']}{Colors.ENDC}")
        print(f"{Colors.CYAN}{ejemplo['comando']}{Colors.ENDC}\n")

# ============================================================================
# EJEMPLOS CON SWAGGER UI
# ============================================================================

def mostrar_swagger():
    """Información sobre Swagger UI"""
    print_header("📚 SWAGGER UI (Interfaz Gráfica)")
    
    print(f"{Colors.CYAN}La forma más fácil de probar los endpoints:{Colors.ENDC}\n")
    
    print(f"1. Asegúrate que el servidor está corriendo:")
    print(f"   {Colors.YELLOW}python -m uvicorn app:app --port 8000{Colors.ENDC}\n")
    
    print(f"2. Abre en tu navegador:")
    print(f"   {Colors.YELLOW}http://127.0.0.1:8000/docs{Colors.ENDC}\n")
    
    print(f"3. Verás todos los endpoints con:")
    print(f"   ✅ Descripción")
    print(f"   ✅ Parámetros")
    print(f"   ✅ Ejemplos")
    print(f"   ✅ Botón para probar\n")
    
    print(f"4. Para cada endpoint:")
    print(f"   • Click en el endpoint")
    print(f"   • Click en 'Try it out'")
    print(f"   • Modifica los valores")
    print(f"   • Click en 'Execute'\n")
    
    print(f"{Colors.GREEN}✅ Verás la respuesta inmediatamente{Colors.ENDC}\n")

# ============================================================================
# TABLA DE BÚSQUEDAS EJEMPLO
# ============================================================================

def mostrar_tabla_busquedas():
    """Muestra tabla de búsquedas comunes"""
    print_header("📊 TABLA DE BÚSQUEDAS COMUNES")
    
    busquedas = [
        ("pasta", "Búsqueda simple con una palabra"),
        ("pasta con tomate", "Dos ingredientes principales"),
        ("receta italiana rápida", "Búsqueda descriptiva completa"),
        ("pollo a la mostaza", "Plato específico"),
        ("comida vegetariana saludable", "Dieta + característica"),
        ("postres dulces sin azúcar", "Tipo de plato + característica"),
        ("receta fácil para principiantes", "Nivel de dificultad"),
        ("cena para 4 personas", "Cantidad de porciones"),
        ("desayuno rápido 10 minutos", "Tiempo + comida del día"),
        ("postre con chocolate", "Ingrediente principal"),
    ]
    
    print(f"{Colors.CYAN}Ejemplos de queries que puedes usar:{Colors.ENDC}\n")
    
    for query, desc in busquedas:
        print(f"  {Colors.YELLOW}'{query}'{Colors.ENDC}")
        print(f"    → {desc}\n")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal"""
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  📖 EJEMPLOS PRÁCTICOS DE BÚSQUEDAS EN EL SERVIDOR  📖  ".center(78) + "║")
    print("║" + "  Recipe Recommender v3".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    print(f"{Colors.ENDC}\n")
    
    # Verificar que servidor está corriendo
    print(f"{Colors.YELLOW}Verificando conexión al servidor...{Colors.ENDC}\n")
    if not test_health():
        return
    
    # Ejemplos de búsquedas
    ejemplo_busqueda_simple()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    ejemplo_busqueda_compleja()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    ejemplo_busqueda_español()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    ejemplo_busqueda_dieta()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    ejemplo_busqueda_tiempo()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    ejemplo_busqueda_ingredientes()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    ejemplo_busqueda_cuisina()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    ejemplo_busqueda_nivel()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Otros endpoints
    ejemplo_info_sistema()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    ejemplo_metricas()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    ejemplo_modelos()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    ejemplo_verificar_reentrenamiento()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Mostrar tabla de búsquedas
    mostrar_tabla_busquedas()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Ejemplos de código
    mostrar_ejemplos_curl()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    mostrar_ejemplos_python()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    mostrar_ejemplos_powershell()
    input(f"{Colors.CYAN}Presiona Enter para continuar...{Colors.ENDC}")
    
    # Swagger
    mostrar_swagger()
    
    # Resumen final
    print_header("✨ RESUMEN FINAL")
    print(f"{Colors.GREEN}✅ Ejemplos completados correctamente{Colors.ENDC}\n")
    print(f"{Colors.CYAN}Ahora puedes:{Colors.ENDC}")
    print(f"  1. Usar Swagger UI en http://127.0.0.1:8000/docs")
    print(f"  2. Hacer requests con curl desde terminal")
    print(f"  3. Usar Python requests para integración")
    print(f"  4. Usar PowerShell en Windows\n")
    print(f"{Colors.GREEN}¡Los datos están listos para ser consultados! 🎉{Colors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Ejecución cancelada{Colors.ENDC}\n")
