#!/usr/bin/env python3
"""
Script para ejecutar la aplicación FastAPI
Ejecuta: python run_app.py [puerto]
"""
import subprocess
import sys
import os
from pathlib import Path

# Raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent

# Puerto por defecto
PORT = sys.argv[1] if len(sys.argv) > 1 else "8000"

# Servidor
SERVER = sys.argv[2] if len(sys.argv) > 2 else "app"

print(f"🚀 Iniciando servidor: src.{SERVER} en puerto {PORT}...")
print(f"📍 URL: http://localhost:{PORT}")
print(f"📚 Docs: http://localhost:{PORT}/docs")

cmd = [
    sys.executable,
    "-m",
    "uvicorn",
    f"src.{SERVER}:app",
    "--host", "0.0.0.0",
    "--port", PORT,
    "--reload"
]

try:
    subprocess.run(cmd, cwd=PROJECT_ROOT)
except KeyboardInterrupt:
    print("\n👋 Servidor detenido")
