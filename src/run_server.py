"""
Script para iniciar el servidor uvicorn con mejor manejo de logs
"""
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
VENV_PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"

print("=" * 60)
print("Iniciando Recipe Recommender API...")
print("=" * 60)

try:
    cmd = [
        str(VENV_PYTHON),
        "-m",
        "uvicorn",
        "app:app",
        "--port", "8000",
        "--host", "127.0.0.1",
        "--log-level", "info"
    ]
    
    print(f"\nComando: {' '.join(cmd)}\n")
    
    process = subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Capturar output línea por línea
    try:
        for line in process.stdout:
            print(line, end='')
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("\n\nShutdown iniciado...")
        process.terminate()
        process.wait(timeout=5)
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
