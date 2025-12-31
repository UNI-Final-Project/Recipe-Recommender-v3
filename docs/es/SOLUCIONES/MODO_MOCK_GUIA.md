# 🎭 MODO MOCK - Guía Rápida

## Qué es el Modo MOCK

Es una versión del servidor que **simula respuestas sin llamar a OpenAI**, perfecto para:
- ✅ Testing rápido
- ✅ Desarrollo local
- ✅ Sin gastar dinero
- ✅ Sin conexión a internet
- ✅ Respuestas instantáneas

---

## 🚀 Iniciar Servidor MOCK

### Opción 1: Directamente (Recomendado)

```powershell
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"

python app_mock.py
```

**Output esperado:**
```
======================================================================
🎭 SERVIDOR DE RECETAS - MODO MOCK
======================================================================
✅ Sin OpenAI - Respuestas simuladas
📊 10 recetas disponibles para testing

🚀 Iniciando servidor...
📍 URL: http://127.0.0.1:8000
📚 Documentación: http://127.0.0.1:8000/docs
======================================================================

INFO:     Uvicorn running on http://127.0.0.1:8000 [press CTRL+C to quit]
```

### Opción 2: Con uvicorn

```powershell
python -m uvicorn app_mock:app --port 8000 --reload
```

---

## 📝 Probar Endpoints

### Método 1: Swagger UI (VISUAL)

1. Abre: http://127.0.0.1:8000/docs
2. Verás interfaz gráfica con todos los endpoints
3. Click en **POST /recommend**
4. Click en **"Try it out"**
5. Ingresa JSON:
```json
{
  "ingredients": ["tomate", "queso"],
  "num_results": 3
}
```
6. Click en **Execute**

### Método 2: PowerShell

**Recomendación simple:**
```powershell
$url = "http://127.0.0.1:8000/recommend"
$body = @{
    query = "pasta"
    num_results = 3
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $url -Method Post `
    -Body $body -ContentType "application/json"

$response | ConvertTo-Json -Depth 5
```

**Con ingredientes:**
```powershell
$url = "http://127.0.0.1:8000/recommend"
$body = @{
    ingredients = @("tomate", "cebolla", "ajo")
    num_results = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri $url -Method Post `
    -Body $body -ContentType "application/json" | 
    ConvertTo-Json -Depth 5
```

### Método 3: cURL

```bash
# Búsqueda simple
curl -X POST "http://127.0.0.1:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query": "sopa", "num_results": 3}'

# Con ingredientes
curl -X POST "http://127.0.0.1:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"ingredients": ["pollo", "limón"], "num_results": 3}'
```

### Método 4: Python

```python
import requests

url = "http://127.0.0.1:8000/recommend"

# Opción A
payload = {
    "query": "pasta",
    "num_results": 3
}

# Opción B (con ingredientes)
payload = {
    "ingredients": ["tomate", "queso"],
    "num_results": 3
}

response = requests.post(url, json=payload)
print(response.json())
```

---

## 📊 Respuesta Típica

```json
{
  "success": true,
  "modo": "🎭 MOCK (sin OpenAI)",
  "query": "pasta",
  "num_resultados": 3,
  "recetas": [
    {
      "nombre": "Espaguetis Clásicos al Pomodoro",
      "descripción": "Receta italiana tradicional con tomates frescos",
      "ingredientes": ["espaguetis", "tomates", "ajo", "aceite", "albahaca"],
      "tiempo_cocina": "30 minutos",
      "porciones": 4,
      "calificacion_promedio": 4.8,
      "num_reviews": 1247,
      "relevancia_score": 0.95
    },
    // ... más recetas
  ],
  "metadata": {
    "tiempo_respuesta_ms": 23,
    "timestamp": "2024-01-15T10:30:45.123456",
    "nota": "Respuestas simuladas para testing"
  }
}
```

---

## 🧪 Ejemplos de Búsquedas

### Búsquedas que funcionan bien:

```powershell
# Estas coinciden con recetas simuladas:
"pasta"           # → 3 recetas de pasta
"tomate"          # → 4 recetas con tomate
"pollo"           # → 2 recetas con pollo
"salmón"          # → 1 receta
"ensalada"        # → 1 receta
"pizza"           # → 1 receta
"sopa"            # → 1 receta
"chocolate"       # → 1 receta (postre)
"tortilla"        # → 1 receta
"rápida"          # → Búsquedas rápidas
"vegetariano"     # → Recetas vegetarianas
"fácil"           # → Recetas fáciles
```

### Crear búsqueda personalizada:

```powershell
# Guión para probar múltiples búsquedas:

$queries = @(
    "pasta",
    "pollo a la mostaza",
    "receta vegetariana",
    "postre",
    "desayuno"
)

foreach ($q in $queries) {
    Write-Host "`n🔍 Buscando: $q" -ForegroundColor Cyan
    
    $body = @{query = $q; num_results = 2} | ConvertTo-Json
    
    $response = Invoke-RestMethod `
        -Uri "http://127.0.0.1:8000/recommend" `
        -Method Post `
        -Body $body `
        -ContentType "application/json"
    
    foreach ($recipe in $response.recetas) {
        Write-Host "  ✓ $($recipe.nombre)" -ForegroundColor Green
        Write-Host "    Rating: ⭐ $($recipe.calificacion_promedio)/5"
    }
}
```

---

## 📚 Todos los Endpoints MOCK

### GET /
**Health check del servidor**
```powershell
Invoke-RestMethod "http://127.0.0.1:8000/"
```

### GET /health
**Estado detallado**
```powershell
Invoke-RestMethod "http://127.0.0.1:8000/health"
```

### GET /recetas
**Ver todas las recetas disponibles**
```powershell
Invoke-RestMethod "http://127.0.0.1:8000/recetas" | 
    ConvertTo-Json -Depth 5
```

### POST /recommend
**Obtener recomendaciones**
```powershell
$body = @{
    ingredients = @("tomate")
    num_results = 3
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/recommend" `
    -Method Post -Body $body -ContentType "application/json"
```

### GET /search?q=pasta&limit=5
**Búsqueda simple**
```powershell
Invoke-RestMethod "http://127.0.0.1:8000/search?q=pasta&limit=3"
```

---

## 🔍 Cómo Funcionan las Respuestas

Las recetas se seleccionan basadas en coincidencias de palabras clave:

```
Query: "pasta"
  ↓
Busca en mapeo: pasta → [índices 0, 1, 2]
  ↓
Retorna 3 recetas de pasta
  ↓
Agrega scores de relevancia simulados
  ↓
Respuesta JSON
```

**Mapeo de palabras clave:**
- `pasta` → Espaguetis, Pasta al Pomodoro, Pasta Cremosa
- `pollo` → Pollo a la Mostaza
- `salmón` → Salmón al Horno
- `ensalada` → Ensalada Griega
- `pizza` → Pizza Casera
- `sopa` → Sopa de Verduras
- `chocolate` → Tarta de Chocolate
- `tortilla` → Tortilla Española

---

## ⚙️ Personalizar Recetas MOCK

Edita `mock_server.py` para agregar más recetas:

```python
MOCK_RECIPES = [
    {
        "nombre": "Mi Receta Nueva",
        "descripción": "...",
        "ingredientes": [...],
        "instrucciones": [...],
        "tiempo_cocina": "30 minutos",
        "porciones": 4,
        "calificacion_promedio": 4.5,
        "num_reviews": 100
    },
    # ... más recetas
]
```

Luego agrega palabras clave en `keyword_map`:

```python
keyword_map = {
    # ...
    "mi_palabra_clave": [índice_de_mi_receta],
}
```

---

## 🔄 Cambiar Entre OpenAI y MOCK

### Usar MOCK:
```powershell
python app_mock.py
```

### Usar OpenAI (si tienes crédito):
```powershell
python -m uvicorn app:app --port 8000
```

---

## ✅ Checklist de Verificación

- [ ] `mock_server.py` existe en el directorio
- [ ] `app_mock.py` existe en el directorio
- [ ] Servidor inicia sin errores
- [ ] Swagger UI carga: http://127.0.0.1:8000/docs
- [ ] GET / devuelve respuesta
- [ ] GET /health devuelve status
- [ ] POST /recommend funciona
- [ ] Respuestas son rápidas (< 100ms)

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'mock_server'"
```powershell
# Asegúrate de estar en el directorio correcto:
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"
python app_mock.py
```

### Error: Puerto 8000 en uso
```powershell
# Cambiar puerto:
python -m uvicorn app_mock:app --port 8001
```

### Las respuestas son lentas
```powershell
# Reiniciar servidor
# (Las respuestas mock deberían ser < 50ms)
```

---

## 📞 Documentos Relacionados

- [SOLUCION_ERROR_429.md](SOLUCION_ERROR_429.md) - Cómo solucionar error 429
- [mock_server.py](mock_server.py) - Código del sistema mock
- [app_mock.py](app_mock.py) - Servidor mock completo
- [EJEMPLOS_BUSQUEDAS.md](EJEMPLOS_BUSQUEDAS.md) - Más ejemplos de búsqueda

---

**¡Listo para testing!** 🚀
