# 🍽️ EJEMPLOS DE BÚSQUEDAS - GUÍA COMPLETA

## 🚀 Cómo empezar

### Paso 1: Iniciar el servidor
```powershell
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"
& "venv\Scripts\python.exe" -m uvicorn app:app --port 8000
```

### Paso 2: Acceder al servidor
Elige una opción:

- **Opción A (Más fácil):** Abre en navegador: http://127.0.0.1:8000/docs
- **Opción B (PowerShell):** Usa los ejemplos de abajo
- **Opción C (Python):** Ejecuta `python ejemplos_busquedas.py`

---

## 📝 EJEMPLOS DE BÚSQUEDAS

### 1️⃣ Búsqueda Simple: Una Palabra

**Query:** `pasta`

#### En Swagger UI
1. Abre http://127.0.0.1:8000/docs
2. Click en "POST /recommend"
3. Click en "Try it out"
4. En el body, escribe:
```json
{
  "query": "pasta"
}
```
5. Click en "Execute"

#### En PowerShell
```powershell
$query = "pasta"
$body = @{ query = $query } | ConvertTo-Json
Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommend" `
  -Method POST `
  -Body $body `
  -ContentType "application/json" | ConvertTo-Json
```

#### En Python
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/recommend",
    json={"query": "pasta"}
)
print(response.json())
```

#### Con cURL
```bash
curl -X POST "http://127.0.0.1:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"query":"pasta"}'
```

---

### 2️⃣ Búsqueda Descriptiva: Frase Completa

**Query:** `Quiero una deliciosa pasta con tomate y ajo`

#### En Swagger UI
```json
{
  "query": "Quiero una deliciosa pasta con tomate y ajo"
}
```

#### En PowerShell
```powershell
$query = "Quiero una deliciosa pasta con tomate y ajo"
$body = @{ query = $query } | ConvertTo-Json
Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommend" `
  -Method POST `
  -Body $body `
  -ContentType "application/json" | ConvertTo-Json
```

**Resultado esperado:** 3 recetas relacionadas con pasta, tomate y ajo

---

### 3️⃣ Búsqueda de Dieta: Vegetariano

**Query:** `Recetas vegetarianas rápidas`

#### En PowerShell (versión compacta)
```powershell
@{query="Recetas vegetarianas rápidas"}|ConvertTo-Json|% {Invoke-WebRequest "http://127.0.0.1:8000/recommend" -Method POST -Body $_ -ContentType "application/json"|ConvertTo-Json}
```

---

### 4️⃣ Búsqueda por Tiempo

**Query:** `Desayuno rápido 5 minutos`

#### En PowerShell
```powershell
@{query="Desayuno rápido 5 minutos"}|ConvertTo-Json|% {Invoke-WebRequest "http://127.0.0.1:8000/recommend" -Method POST -Body $_ -ContentType "application/json"}
```

---

### 5️⃣ Búsqueda por Ingrediente Específico

**Query:** `Salmón con limón y aceite de oliva`

#### En PowerShell
```powershell
$query = "Salmón con limón y aceite de oliva"
$body = @{ query = $query } | ConvertTo-Json
$response = Invoke-WebRequest "http://127.0.0.1:8000/recommend" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"

$data = $response.Content | ConvertFrom-Json
$data.recetas | ForEach-Object {
  Write-Host "- $($_.nombre) (⭐ $($_.calificacion_promedio)/5)"
}
```

---

### 6️⃣ Búsqueda por Tipo de Cocina

**Query:** `Recetas italianas auténticas`

#### En PowerShell
```powershell
@{query="Recetas italianas auténticas"}|ConvertTo-Json|% {Invoke-WebRequest "http://127.0.0.1:8000/recommend" -Method POST -Body $_ -ContentType "application/json"|ConvertTo-Json}
```

---

### 7️⃣ Búsqueda por Nivel de Dificultad

**Query:** `Receta fácil para principiantes`

#### En PowerShell
```powershell
@{query="Receta fácil para principiantes"}|ConvertTo-Json|% {Invoke-WebRequest "http://127.0.0.1:8000/recommend" -Method POST -Body $_ -ContentType "application/json"}
```

---

### 8️⃣ Búsqueda Específica: Plato Nombrado

**Query:** `Pollo a la mostaza`

#### En PowerShell
```powershell
@{query="Pollo a la mostaza"}|ConvertTo-Json|% {Invoke-WebRequest "http://127.0.0.1:8000/recommend" -Method POST -Body $_ -ContentType "application/json"}
```

---

### 9️⃣ Búsqueda Especial: Postres

**Query:** `Postre de chocolate sin horno`

#### En PowerShell
```powershell
$query = "Postre de chocolate sin horno"
@{ query = $query } | ConvertTo-Json | `
  % { Invoke-WebRequest "http://127.0.0.1:8000/recommend" `
    -Method POST -Body $_ -ContentType "application/json" } | `
  Select-Object -ExpandProperty Content | ConvertFrom-Json
```

---

### 🔟 Búsqueda Larga y Descriptiva

**Query:** `Necesito una cena especial, algo elegante pero que no tarde mucho en preparar, para impresionar a mi pareja`

#### En PowerShell
```powershell
$query = "Necesito una cena especial, algo elegante pero que no tarde mucho en preparar, para impresionar a mi pareja"
$body = @{ query = $query } | ConvertTo-Json
Invoke-WebRequest "http://127.0.0.1:8000/recommend" `
  -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json
```

---

## 📊 OTROS ENDPOINTS

### Verificar Salud del Servidor

**GET /health** - ¿Está el servidor funcionando?

#### En Swagger UI
Click en "GET /health" → "Try it out" → "Execute"

#### En PowerShell
```powershell
Invoke-WebRequest "http://127.0.0.1:8000/health" | ConvertTo-Json
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "num_recipes": 53064,
  "model_production": "hybrid_ranker v1.0.0"
}
```

---

### Ver Información del Sistema

**GET /** - ¿Qué información expone el API?

#### En Swagger UI
Click en "GET /" → "Try it out" → "Execute"

#### En PowerShell
```powershell
Invoke-WebRequest "http://127.0.0.1:8000/" | ConvertTo-Json
```

---

### Ver Métricas en Tiempo Real

**GET /metrics** - ¿Cómo está performando el sistema?

#### En Swagger UI
Click en "GET /metrics" → "Try it out" → "Execute"

#### En PowerShell
```powershell
$response = Invoke-WebRequest "http://127.0.0.1:8000/metrics"
$data = $response.Content | ConvertFrom-Json
Write-Host "Total requests: $($data.metrics.total_requests)"
Write-Host "Avg latency: $($data.metrics.avg_latency_ms)ms"
Write-Host "Error rate: $($data.metrics.error_rate)%"
```

**Información que verás:**
- Total requests procesados
- Latencia promedio
- Tasa de error
- Percentiles (p50, p95, p99)

---

### Ver Modelos Disponibles

**GET /models** - ¿Qué modelos están registrados?

#### En PowerShell
```powershell
Invoke-WebRequest "http://127.0.0.1:8000/models" | ConvertTo-Json
```

**Respuesta esperada:**
```json
{
  "models": [
    {
      "model_id": "hybrid_ranker",
      "version": "1.0.0",
      "status": "production"
    }
  ]
}
```

---

### Verificar si el Modelo Necesita Reentrenamiento

**POST /retrain/check** - ¿Necesita reentrenamiento?

#### En PowerShell
```powershell
Invoke-WebRequest "http://127.0.0.1:8000/retrain/check" -Method POST | ConvertTo-Json
```

---

## 🎯 TABLA DE BÚSQUEDAS COMUNES

| Query | Tipo | Descripción |
|-------|------|-------------|
| `pasta` | Simple | Una palabra |
| `pasta con tomate` | Dos ingredientes | Ingredientes principales |
| `Pollo a la mostaza` | Plato específico | Nombre de plato |
| `Receta vegetariana` | Dieta | Tipo de alimentación |
| `Desayuno rápido` | Tiempo + comida | Tiempo + momento del día |
| `Postres sin azúcar` | Característica | Restricción dietética |
| `Comida italiana` | Cocina | País/región origen |
| `Receta fácil` | Dificultad | Nivel de destreza |
| `Salmón al horno` | Ingrediente + forma | Ingrediente + preparación |
| `Cena para 4 personas` | Porciones | Cantidad |

---

## 💡 FUNCIÓN AUXILIAR (Copiar una sola vez)

Una vez copies esto en PowerShell, puedes reutilizarlo:

```powershell
function Search-Recipe {
  param([string]$Query)
  
  $body = @{ query = $Query } | ConvertTo-Json
  $response = Invoke-WebRequest "http://127.0.0.1:8000/recommend" `
    -Method POST -Body $body -ContentType "application/json"
  
  $data = $response.Content | ConvertFrom-Json
  
  Write-Host "`n🔍 Recetas para: '$Query'" -ForegroundColor Green
  Write-Host "─────────────────────────────────────" -ForegroundColor Green
  
  if ($data.recetas.Count -eq 0) {
    Write-Host "No se encontraron recetas" -ForegroundColor Yellow
    return
  }
  
  $data.recetas | ForEach-Object {
    Write-Host "`n📖 $($_.nombre)" -ForegroundColor Yellow
    Write-Host "   ⭐ Rating: $($_.calificacion_promedio)/5" -ForegroundColor Cyan
    if ($_.tiempo_cocina) {
      Write-Host "   ⏱️  Tiempo: $($_.tiempo_cocina)" -ForegroundColor Cyan
    }
    if ($_.porciones) {
      Write-Host "   🍽️  Porciones: $($_.porciones)" -ForegroundColor Cyan
    }
  }
  
  Write-Host "`n"
}

# Ahora puedes usar:
Search-Recipe "pasta"
Search-Recipe "pollo al horno"
Search-Recipe "postre de chocolate"
```

---

## 🔄 BÚSQUEDA INTERACTIVA CONTINUA

```powershell
while ($true) {
  Write-Host ""
  $query = Read-Host "🔍 Ingresa tu búsqueda (o 'salir' para terminar)"
  
  if ($query -eq "salir") { 
    Write-Host "`nHasta luego! 👋" -ForegroundColor Green
    break 
  }
  
  if ([string]::IsNullOrWhiteSpace($query)) {
    Write-Host "Por favor ingresa una búsqueda válida" -ForegroundColor Yellow
    continue
  }
  
  try {
    $body = @{ query = $query } | ConvertTo-Json
    $response = Invoke-WebRequest "http://127.0.0.1:8000/recommend" `
      -Method POST -Body $body -ContentType "application/json" `
      -ErrorAction Stop
    
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "`n✨ Resultados para: '$query'" -ForegroundColor Green
    Write-Host "──────────────────────────────" -ForegroundColor Green
    
    if ($data.recetas.Count -eq 0) {
      Write-Host "No se encontraron recetas" -ForegroundColor Yellow
    } else {
      $data.recetas | ForEach-Object {
        Write-Host "  • $($_.nombre) ⭐ $($_.calificacion_promedio)/5" -ForegroundColor Cyan
      }
    }
  }
  catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
  }
}
```

---

## 🧪 SCRIPT DE TESTING AUTOMÁTICO

```powershell
# Script para hacer 10 búsquedas automáticas

$queries = @(
  "pasta",
  "pollo al limón",
  "postre de chocolate",
  "salmón al horno",
  "ensalada griega",
  "pizza italiana",
  "sopa de verduras",
  "desayuno rápido",
  "comida vegana",
  "tarta fría"
)

Write-Host "Realizando 10 búsquedas de prueba..." -ForegroundColor Green

$queries | ForEach-Object -Begin { $count = 1 } -Process {
  Write-Host "`n[$count/10] Buscando: $_" -ForegroundColor Yellow
  
  $body = @{ query = $_ } | ConvertTo-Json
  $response = Invoke-WebRequest "http://127.0.0.1:8000/recommend" `
    -Method POST -Body $body -ContentType "application/json"
  
  $data = $response.Content | ConvertFrom-Json
  Write-Host "       ✅ Se encontraron $($data.recetas.Count) recetas" -ForegroundColor Green
  
  $count++
}

Write-Host "`n✨ Test completado!" -ForegroundColor Green
```

---

## 🎓 TIPS Y TRUCOS

### Búsquedas Efectivas
- ✅ Sé descriptivo: `pollo al limón` es mejor que solo `pollo`
- ✅ Incluye características: `receta rápida`, `saludable`, `vegana`
- ✅ Menciona ingredientes principales
- ✅ Especifica el tipo de comida: `desayuno`, `almuerzo`, `cena`, `postre`

### Búsquedas Menos Efectivas
- ❌ Muy genéricas: solo `comida`
- ❌ Palabras aisladas sin contexto
- ❌ Ortografía inconsistente (aunque el sistema es bastante robusto)

### Performance
- ⏱️ Tiempo de respuesta: típicamente **200-300ms**
- 🔄 El sistema puede manejar múltiples requests concurrentes
- 💾 Se cachean los embeddings para búsquedas similares

---

## 🎉 ¡LISTO!

Ya sabes cómo hacer búsquedas. Elige tu método preferido:

1. **Swagger UI** (más fácil) → http://127.0.0.1:8000/docs
2. **PowerShell** (más rápido) → Copia los ejemplos
3. **Python** (para integración) → `python ejemplos_busquedas.py`
4. **cURL** (para scripts) → Usa los comandos curl

¡Disfruta buscando recetas! 🍽️
