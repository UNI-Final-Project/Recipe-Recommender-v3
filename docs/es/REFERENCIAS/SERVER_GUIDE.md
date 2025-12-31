# 🚀 Guía de Operación del Servidor MLOps Recipe Recommender

## Estado Actual ✅

El servidor FastAPI con sistema MLOps está **operativo y corriendo** en:
- **URL:** `http://127.0.0.1:8000`
- **Proceso:** uvicorn
- **Puerto:** 8000
- **Datos:** 53,064 recetas cargadas
- **Modelo:** hybrid_ranker v1.0.0 en producción

---

## Iniciar el Servidor

### Opción 1: Comando Simple (Recomendado)

```powershell
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"
& "venv\Scripts\python.exe" -m uvicorn app:app --port 8000 --host 127.0.0.1
```

### Opción 2: Con Recarga Automática (Desarrollo)

```powershell
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"
& "venv\Scripts\python.exe" -m uvicorn app:app --port 8000 --reload
```

### Opción 3: Script Python

```powershell
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"
& "venv\Scripts\python.exe" run_server.py
```

---

## Endpoints Disponibles

### 1. GET `/health` - Health Check
```bash
curl http://127.0.0.1:8000/health
```

### 2. POST `/recommend` - Obtener Recomendaciones
```bash
curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "delicious pasta with tomato"}'
```

### 3. GET `/metrics` - Obtener Métricas
```bash
curl http://127.0.0.1:8000/metrics
```

### 4. GET `/models` - Listar Modelos Registrados
```bash
curl http://127.0.0.1:8000/models
```

### 5. GET `/models/{id}/production` - Detalles del Modelo
```bash
curl http://127.0.0.1:8000/models/hybrid_ranker/production
```

### 6. POST `/retrain/check` - Verificar Necesidad de Retraining
```bash
curl -X POST http://127.0.0.1:8000/retrain/check
```

---

## Documentación Interactiva

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## Troubleshooting

### El puerto 8000 ya está en uso

```powershell
# Encontrar el proceso usando el puerto 8000
netstat -ano | Select-String "8000"

# Matar el proceso (reemplazar PID con el número real)
Stop-Process -Id <PID> -Force
```

### MLflow Warnings

Los warnings sobre archivos YAML faltantes en MLflow son **normales y no afectan la funcionalidad**. Se pueden ignorar.

### Verificar que el servidor está corriendo

```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method Get
$response.Content | ConvertFrom-Json
```

---

## Monitoreo

### Ver logs en tiempo real

```powershell
# El terminal mostrará todos los logs mientras está corriendo
# Presiona Ctrl+C para detener
```

### Acceder a MLflow UI

```bash
mlflow ui --backend-store-uri ./mlruns
```

Luego accede a: `http://127.0.0.1:5000`

---

## Detener el Servidor

```powershell
# En el terminal donde está corriendo, presiona:
Ctrl + C
```

---

## Resumen de Correcciones Realizadas

✅ Reparado error de variables no definidas en `app.py`
✅ Corregido atributo faltante en `retraining.py`
✅ Agregado `check_compatibility=False` en cliente Qdrant
✅ Mejorado manejo de excepciones en startup
✅ Eliminado código duplicado de MLflow
✅ El servidor ahora inicia y se mantiene estable

---

**Fecha:** 31 de Diciembre de 2025
**Estado:** ✅ OPERATIVO
