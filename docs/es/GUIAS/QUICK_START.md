# ⚡ QUICK START - Flujo Completo en 5 Minutos

## 1️⃣ Preparar el Entorno (30 segundos)

```powershell
# Abrir terminal PowerShell en el proyecto
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"

# Activar virtual environment
& "venv\Scripts\Activate.ps1"
```

---

## 2️⃣ Iniciar el Servidor (20 segundos)

```powershell
# Opción A: Modo producción (recomendado)
& "venv\Scripts\python.exe" -m uvicorn app:app --port 8000

# Opción B: Modo desarrollo (con auto-reload)
& "venv\Scripts\python.exe" -m uvicorn app:app --port 8000 --reload
```

**Esperado:**
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
2025-12-31 00:19:17,849 - app - INFO - Data loaded: 53064 recipes
2025-12-31 00:19:18,057 - mlops - INFO - MLOps system initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 3️⃣ Acceder a Swagger UI (10 segundos)

**URL:** http://127.0.0.1:8000/docs

**Verás una interfaz interactiva con todos los endpoints.**

---

## 4️⃣ Probar Recomendaciones (2 minutos)

### Opción A: Usando Swagger UI (Easiest)

1. Click en **"POST /recommend"**
2. Click en **"Try it out"**
3. Reemplaza el JSON con:
```json
{
  "query": "delicious pasta with tomato"
}
```
4. Click en **"Execute"**
5. Ver respuesta con 3 recetas

### Opción B: Usando PowerShell

```powershell
$body = @{
    query = "delicious pasta with tomato"
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommend" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Opción C: Usando curl

```bash
curl -X POST "http://127.0.0.1:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "delicious pasta with tomato"}'
```

---

## 5️⃣ Explorar Otros Endpoints (1-2 minutos)

En la misma página Swagger UI, expande cada endpoint:

### Health Check
```
GET /health → Click Execute
```
Verás estado del sistema, recetas cargadas, modelo en producción.

### Metrics
```
GET /metrics → Click Execute
```
Verás latencias, tasa de error, requests por endpoint.

### Models
```
GET /models → Click Execute
```
Verás lista de modelos registrados con versiones.

### Model Details
```
GET /models/hybrid_ranker/production → Click Execute
```
Verás parámetros, descripción, features del modelo.

### Retraining Check
```
POST /retrain/check → Click Execute
```
Verás si hay modelos que necesitan retraining.

---

## 🎯 Respuesta Esperada: Recomendaciones

```json
{
  "recetas": [
    {
      "nombre": "Classic Spaghetti al Pomodoro",
      "descripción": "Traditional Italian pasta with fresh tomato sauce",
      "ingredientes": [
        "spaghetti",
        "tomatoes", 
        "garlic",
        "olive oil",
        "basil"
      ],
      "instrucciones": [
        "Cook pasta",
        "Prepare sauce", 
        "Combine"
      ],
      "calificación_promedio": 4.8
    },
    {
      "nombre": "Garlic Pasta with Herbs",
      "descripción": "Simple but flavorful garlic pasta dish",
      "ingredientes": [
        "pasta",
        "garlic",
        "herbs",
        "oil"
      ],
      "instrucciones": [
        "Cook pasta",
        "Sauté garlic"
      ],
      "calificación_promedio": 4.5
    },
    {
      "nombre": "Creamy Tomato Pasta",
      "descripción": "Rich and creamy pasta with tomato",
      "ingredientes": [
        "pasta",
        "tomato",
        "cream",
        "garlic"
      ],
      "instrucciones": [
        "Cook pasta",
        "Make sauce"
      ],
      "calificación_promedio": 4.6
    }
  ]
}
```

---

## 📊 Respuesta Esperada: Health Check

```json
{
  "status": "healthy",
  "timestamp": "2025-12-31T00:19:18.057000",
  "service": "Recipe Recommender API",
  "version": "1.0.0",
  "data_loaded": true,
  "num_recipes": 53064,
  "model_production": "hybrid_ranker v1.0.0"
}
```

---

## 📈 Respuesta Esperada: Metrics

```json
{
  "total_requests": 5,
  "avg_latency_ms": 245.5,
  "error_rate": 0.0,
  "requests_by_endpoint": {
    "/recommend": 3,
    "/health": 2
  },
  "performance_metrics": {
    "p50_latency": 200,
    "p95_latency": 400,
    "p99_latency": 800
  }
}
```

---

## 🔍 Respuesta Esperada: Models

```json
{
  "models": [
    {
      "model_id": "hybrid_ranker",
      "version": "1.0.0",
      "status": "production",
      "model_type": "hybrid",
      "created_at": "2025-12-31T00:19:18",
      "metrics": {
        "alpha": 0.7,
        "status": "production"
      }
    }
  ]
}
```

---

## 🛠️ Solucionar Problemas

### Problema: "Connection refused"
```
Solución: Asegúrate que el servidor está corriendo
          (deberías ver "Uvicorn running on http://127.0.0.1:8000")
```

### Problema: "Port already in use"
```powershell
# Mata el proceso anterior
Get-Process -Name python | Stop-Process -Force
Start-Sleep -Seconds 2

# Intenta de nuevo
& "venv\Scripts\python.exe" -m uvicorn app:app --port 8000
```

### Problema: "ModuleNotFoundError"
```powershell
# Instala dependencias
pip install -r requirements.txt
```

### Problema: "No .env file"
```
Solución: Crea .env con tus API keys
          Ver template: .env.example
```

---

## 📚 Documentación Adicional

Después de probar, lee estos documentos:

1. **COMPLETE_FLOW.md** - Flujo detallado con arquitectura
2. **SERVER_GUIDE.md** - Cómo operar el servidor
3. **MLOPS_GUIDE.md** - Detalles técnicos
4. **EXECUTIVE_SUMMARY.md** - Resumen ejecutivo

---

## ✅ Checklist

- [ ] Terminal abierta en el proyecto
- [ ] Virtual environment activado
- [ ] Servidor iniciado (veo "Uvicorn running...")
- [ ] Accedí a Swagger UI (/docs)
- [ ] Probé /recommend
- [ ] Probé /health
- [ ] Probé /metrics
- [ ] Vi respuestas correctas

---

## 🎓 Lo que Acabas de Demostrar

✅ **Sistema de Recomendaciones Inteligente**
- Búsqueda semántica con embeddings
- Ranking híbrido
- 53K opciones disponibles

✅ **MLOps en Producción**
- Tracking de experimentos
- Versionado de modelos
- Monitoreo automático

✅ **API Enterprise-Grade**
- FastAPI moderno
- Documentación automática
- Manejo robusto de errores

---

## 🚀 Próximo Paso

**Ve a http://127.0.0.1:8000/docs y comienza a experimentar!**

¡El sistema está listo para usar! 🎉

---

**Tiempo Total:** ~5 minutos
**Complejidad:** Muy fácil
**Resultado:** Sistema MLOps completo funcionando
