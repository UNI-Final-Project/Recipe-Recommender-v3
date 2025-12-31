"""
Configuración de pytest para el proyecto Recipe Recommender
"""
import sys
from pathlib import Path

# Agregar el directorio src al path para que los imports funcionen
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import pytest


@pytest.fixture(scope="session")
def app_root():
    """Retorna la raíz del proyecto"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def src_root():
    """Retorna la carpeta src"""
    return PROJECT_ROOT / "src"
