#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE REORGANIZACIÓN AUTOMÁTICA
===================================

Este script reorganiza el proyecto según la estructura modular profesional.

Uso:
    python reorganize_project.py
    
O si quieres ver qué va a hacer sin ejecutar:
    python reorganize_project.py --dry-run
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
import sys

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
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

# Mapeo de archivos a reorganizar
FILES_TO_MOVE = {
    # Código Python → src/
    'app.py': 'src/app.py',
    'app_mock.py': 'src/app_mock.py',
    'mock_server.py': 'src/mock_server.py',
    'run_server.py': 'src/run_server.py',
    'schedule_retraining.py': 'src/schedule_retraining.py',
    
    # Tests → tests/
    'test_flow.py': 'tests/test_api.py',
    'test_mock_server.py': 'tests/test_mock.py',
    'test_mlops.py': 'tests/test_mlops.py',
    'test_api.ps1': 'tests/test_api.ps1',
    
    # Documentación de Inicio → docs/es/
    'README.md': 'docs/es/README.md',
    'INICIO_AQUI.txt': 'docs/es/INICIO_AQUI.txt',
    'INDICE_RAPIDO.txt': 'docs/es/INDICE_RAPIDO.txt',
    'QUICK_START.md': 'docs/es/GUIAS/QUICK_START.md',
    'QUICKSTART.md': 'docs/es/GUIAS/QUICKSTART.md',
    'README_MOCK_SETUP.md': 'docs/es/GUIAS/README_MOCK_SETUP.md',
    
    # Documentación de Soluciones → docs/es/SOLUCIONES/
    'SOLUCION_ERROR_429.md': 'docs/es/SOLUCIONES/SOLUCION_ERROR_429.md',
    'SOLUCION_COMPLETADA.md': 'docs/es/SOLUCIONES/SOLUCION_COMPLETADA.md',
    'MODO_MOCK_GUIA.md': 'docs/es/SOLUCIONES/MODO_MOCK_GUIA.md',
    'COMPARACION_APP_VERSIONS.md': 'docs/es/SOLUCIONES/COMPARACION_APP_VERSIONS.md',
    'RESUMEN_VISUAL_SOLUCIONES.md': 'docs/es/SOLUCIONES/RESUMEN_VISUAL_SOLUCIONES.md',
    
    # Documentación de Referencia → docs/es/REFERENCIAS/
    'SERVER_GUIDE.md': 'docs/es/REFERENCIAS/SERVER_GUIDE.md',
    'MLOPS_GUIDE.md': 'docs/es/REFERENCIAS/MLOPS_GUIDE.md',
    'MLOPS_IMPLEMENTATION.md': 'docs/es/REFERENCIAS/MLOPS_IMPLEMENTATION.md',
    
    # Documentación de Arquitectura → docs/es/ARQUITECTURA/
    'MAPA_SOLUCION.md': 'docs/es/ARQUITECTURA/MAPA_SOLUCION.md',
    'MAPA_NAVEGACION.md': 'docs/es/ARQUITECTURA/MAPA_NAVEGACION.md',
    'COMPLETE_FLOW.md': 'docs/es/ARQUITECTURA/COMPLETE_FLOW.md',
    'COMPLETE_DATA_FLOW.md': 'docs/es/ARQUITECTURA/COMPLETE_DATA_FLOW.md',
    
    # Documentación de Índices → docs/es/INDICE/
    'INDICE_SOLUCIONES_429.md': 'docs/es/INDICE/INDICE_SOLUCIONES_429.md',
    'DOCUMENTATION_INDEX.md': 'docs/es/INDICE/DOCUMENTATION_INDEX.md',
    'DOCUMENTATION_INDEX_ES.md': 'docs/es/INDICE/DOCUMENTATION_INDEX_ES.md',
    'INDEX.md': 'docs/es/INDICE/INDEX.md',
    'INVENTARIO_COMPLETO.md': 'docs/es/INDICE/INVENTARIO_COMPLETO.md',
    
    # Documentación General → docs/es/GENERAL/
    'EXECUTIVE_SUMMARY.md': 'docs/es/GENERAL/EXECUTIVE_SUMMARY.md',
    'FINAL_STATUS.md': 'docs/es/GENERAL/FINAL_STATUS.md',
    'FIXES_SUMMARY.md': 'docs/es/GENERAL/FIXES_SUMMARY.md',
    'VERIFICACION_FINAL.md': 'docs/es/GENERAL/VERIFICACION_FINAL.md',
    'VISUAL_SUMMARY.md': 'docs/es/GENERAL/VISUAL_SUMMARY.md',
    'RESUMEN_VISUAL_FINAL.md': 'docs/es/GENERAL/RESUMEN_VISUAL_FINAL.md',
    'CHECKLIST.md': 'docs/es/GENERAL/CHECKLIST.md',
    
    # Ejemplos → examples/
    'ejemplos_busquedas.py': 'examples/python/ejemplos_busquedas.py',
    'ejemplos_busquedas.ps1': 'examples/powershell/ejemplos_busquedas.ps1',
    'flujo_completo_demo.py': 'examples/python/flujo_completo_demo.py',
    'EJEMPLOS_BUSQUEDAS.md': 'examples/EJEMPLOS_BUSQUEDAS.md',
    
    # Config
    '.env': 'config/.env',
}

# Directorios a crear
DIRECTORIES_TO_CREATE = [
    'src',
    'config',
    'docs',
    'docs/es',
    'docs/es/GUIAS',
    'docs/es/REFERENCIAS',
    'docs/es/SOLUCIONES',
    'docs/es/ARQUITECTURA',
    'docs/es/INDICE',
    'docs/es/GENERAL',
    'docs/en',
    'examples',
    'examples/python',
    'examples/powershell',
    'examples/curl',
    'tests',
]

def create_init_files(base_path: str):
    """Crear archivos __init__.py en carpetas Python"""
    init_dirs = ['src', 'mlops', 'tests']
    for dir_name in init_dirs:
        init_file = os.path.join(base_path, dir_name, '__init__.py')
        if not os.path.exists(init_file):
            Path(init_file).touch()
            print_success(f"Creado {init_file}")

def reorganize_project(base_path: str, dry_run: bool = False):
    """
    Reorganiza el proyecto
    """
    print_header("🔄 REORGANIZACIÓN DEL PROYECTO")
    
    # Paso 1: Crear directorios
    print_info("Paso 1: Creando estructura de directorios...")
    for dir_name in DIRECTORIES_TO_CREATE:
        dir_path = os.path.join(base_path, dir_name)
        if not os.path.exists(dir_path):
            if not dry_run:
                os.makedirs(dir_path, exist_ok=True)
            print_success(f"Directorio: {dir_name}")
        else:
            print_info(f"Ya existe: {dir_name}")
    
    # Crear __init__.py
    if not dry_run:
        create_init_files(base_path)
    
    # Paso 2: Mover archivos
    print_info("\nPaso 2: Moviendo archivos...")
    moved_count = 0
    failed_count = 0
    
    for old_name, new_path in FILES_TO_MOVE.items():
        old_path = os.path.join(base_path, old_name)
        new_full_path = os.path.join(base_path, new_path)
        
        # Crear directorio si no existe
        new_dir = os.path.dirname(new_full_path)
        if not os.path.exists(new_dir):
            if not dry_run:
                os.makedirs(new_dir, exist_ok=True)
        
        # Mover archivo
        if os.path.exists(old_path):
            try:
                if not dry_run:
                    shutil.move(old_path, new_full_path)
                print_success(f"{old_name} → {new_path}")
                moved_count += 1
            except Exception as e:
                print_error(f"Error moviendo {old_name}: {e}")
                failed_count += 1
        else:
            print_info(f"No encontrado: {old_name}")
    
    # Resumen
    print_header("📊 RESUMEN")
    print(f"{Colors.GREEN}✅ Archivos movidos: {moved_count}{Colors.RESET}")
    if failed_count > 0:
        print(f"{Colors.RED}❌ Errores: {failed_count}{Colors.RESET}")
    
    if dry_run:
        print_warning("Modo dry-run: nada fue modificado")
    else:
        print_success("¡Reorganización completada!")
    
    print_info("Estructura creada:")
    print("""
    📁 src/              ← Código Python
    📁 config/           ← Configuración
    📁 docs/es/          ← Documentación Español
    📁 docs/en/          ← Documentación Inglés
    📁 examples/         ← Ejemplos
    📁 tests/            ← Tests
    📁 mlops/            ← MLOps (ya existía)
    📁 data/             ← Datos
    📁 models/           ← Modelos
    📁 mlruns/           ← MLflow
    """)

def create_navigation_index(base_path: str):
    """Crear archivo de índice de navegación"""
    print_info("\nCreando índice de navegación...")
    
    index_content = """# 📑 ÍNDICE DE NAVEGACIÓN

## 🎯 Inicio Rápido
- **Primeros Pasos:** docs/es/INICIO_AQUI.txt
- **Setup:** docs/es/GUIAS/QUICK_START.md
- **Solución Error 429:** docs/es/SOLUCIONES/SOLUCION_ERROR_429.md

## 💻 Desarrollo
- **Código:** src/
- **Tests:** tests/
- **Ejemplos:** examples/

## 📚 Documentación
- **Guías:** docs/es/GUIAS/
- **Referencias:** docs/es/REFERENCIAS/
- **Soluciones:** docs/es/SOLUCIONES/
- **Arquitectura:** docs/es/ARQUITECTURA/

## 🔧 Configuración
- **Config:** config/
- **MLOps:** mlops/

## 📦 Datos
- **Data:** data/
- **Models:** models/
- **MLflow:** mlruns/

---

## 📍 Ubicación de Archivos

| Tipo | Ubicación | Ejemplo |
|------|-----------|---------|
| Código | src/ | app.py, mock_server.py |
| Tests | tests/ | test_api.py, test_mock.py |
| Docs | docs/es/ | GUIAS/, REFERENCIAS/ |
| Ejemplos | examples/ | python/, powershell/ |
| Config | config/ | settings.py, .env |
| MLOps | mlops/ | monitoring.py, retraining.py |
| Datos | data/ | food.pkl |

---

Ver: ESTRUCTURA_PROYECTO.md para más detalles
"""
    
    index_path = os.path.join(base_path, 'docs', 'es', 'NAVEGACION.md')
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print_success(f"Índice creado: {index_path}")

def main():
    """Función principal"""
    base_path = os.getcwd()
    dry_run = '--dry-run' in sys.argv
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}REORGANIZACIÓN DE PROYECTO RECIPE-RECOMMENDER{Colors.RESET}")
    print(f"Directorio base: {base_path}")
    
    if dry_run:
        print_warning("Ejecutando en modo DRY-RUN (sin cambios reales)")
    
    input(f"\n{Colors.YELLOW}Presiona Enter para continuar...{Colors.RESET}")
    
    # Ejecutar reorganización
    reorganize_project(base_path, dry_run)
    
    # Crear índice de navegación
    if not dry_run:
        create_navigation_index(base_path)
    
    print_header("✅ REORGANIZACIÓN COMPLETADA")
    print(f"""
{Colors.GREEN}
Próximos pasos:
1. Revisar nueva estructura: docs/es/NAVEGACION.md
2. Actualizar imports en código
3. Actualizar referencias en documentación
4. Actualizar CI/CD pipelines
{Colors.RESET}
    """)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrumpido por el usuario{Colors.RESET}")
    except Exception as e:
        print_error(f"Error: {e}")
