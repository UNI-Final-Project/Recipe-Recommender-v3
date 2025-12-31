# EJEMPLOS DE BÚSQUEDAS EN POWERSHELL
# ===================================
# 
# Este archivo contiene ejemplos listos para copiar y pegar en PowerShell
# para hacer búsquedas en el servidor Recipe Recommender

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║     📖 EJEMPLOS DE BÚSQUEDAS EN POWERSHELL 📖                  ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Primero, asegúrate de que el servidor está corriendo:" -ForegroundColor Yellow
Write-Host 'python -m uvicorn app:app --port 8000' -ForegroundColor Cyan
Write-Host "`nLuego, copia y pega los ejemplos a continuación:` -ForegroundColor White

# ============================================================================
# BÚSQUEDA 1: Pasta simple
# ============================================================================
Write-Host "`n" -ForegroundColor White
Write-Host "1️⃣  BÚSQUEDA SIMPLE: 'pasta'" -ForegroundColor Yellow
Write-Host "════════════════════════════════" -ForegroundColor Yellow
Write-Host "`nCopia esto en PowerShell:`n" -ForegroundColor Cyan

$ejemplo1 = @'
$query = "pasta"
$body = @{ query = $query } | ConvertTo-Json
Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommend" `
  -Method POST `
  -Body $body `
  -ContentType "application/json" | ConvertTo-Json
'@

Write-Host $ejemplo1 -ForegroundColor White

Write-Host "`nO de forma compacta:`n" -ForegroundColor Cyan
Write-Host '@{query="pasta"}|ConvertTo-Json|% {Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommend" -Method POST -Body $_ -ContentType "application/json"}|ConvertTo-Json' -ForegroundColor White

# ============================================================================
# BÚSQUEDA 2: Pasta con tomate
# ============================================================================
Write-Host "`n`n" -ForegroundColor White
Write-Host "2️⃣  BÚSQUEDA DESCRIPTIVA: 'Pasta con tomate y ajo'" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "`n" -ForegroundColor Cyan

$ejemplo2 = @'
$query = "Pasta con tomate y ajo"
$body = @{ query = $query } | ConvertTo-Json
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommend" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"

$data = $response.Content | ConvertFrom-Json
Write-Host "Se encontraron $($data.recetas.Count) recetas:" -ForegroundColor Green
$data.recetas | ForEach-Object {
  Write-Host "  - $($_.nombre)" -ForegroundColor Yellow
  Write-Host "    Rating: $($_.calificacion_promedio)/5" -ForegroundColor Cyan
}
'@

Write-Host $ejemplo2 -ForegroundColor White

# ============================================================================
# BÚSQUEDA 3: Vegano
# ============================================================================
Write-Host "`n`n" -ForegroundColor White
Write-Host "3️⃣  BÚSQUEDA DIETA: 'Receta vegana saludable'" -ForegroundColor Yellow
Write-Host "═════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "`n" -ForegroundColor Cyan

$ejemplo3 = @'
$query = "Receta vegana saludable"
@{ query = $query } | ConvertTo-Json | `
  % { Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommend" `
    -Method POST -Body $_ -ContentType "application/json" } | `
  Select-Object -ExpandProperty Content | ConvertFrom-Json
'@

Write-Host $ejemplo3 -ForegroundColor White

# ============================================================================
# BÚSQUEDA 4: Desayuno
# ============================================================================
Write-Host "`n`n" -ForegroundColor White
Write-Host "4️⃣  BÚSQUEDA TIEMPO: 'Desayuno rápido 5 minutos'" -ForegroundColor Yellow
Write-Host "═════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "`n" -ForegroundColor Cyan

Write-Host '@{query="Desayuno rápido 5 minutos"}|ConvertTo-Json|% {Invoke-WebRequest "http://127.0.0.1:8000/recommend" -Method POST -Body $_ -ContentType "application/json"|ConvertTo-Json}' -ForegroundColor White

# ============================================================================
# BÚSQUEDA 5: Pollo
# ============================================================================
Write-Host "`n`n" -ForegroundColor White
Write-Host "5️⃣  BÚSQUEDA INGREDIENTE: 'Pollo al limón'" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "`n" -ForegroundColor Cyan

Write-Host '@{query="Pollo al limón"}|ConvertTo-Json|% {Invoke-WebRequest "http://127.0.0.1:8000/recommend" -Method POST -Body $_ -ContentType "application/json"|ConvertTo-Json}' -ForegroundColor White

# ============================================================================
# HEALTH CHECK
# ============================================================================
Write-Host "`n`n" -ForegroundColor White
Write-Host "6️⃣  VERIFICAR SALUD DEL SERVIDOR" -ForegroundColor Yellow
Write-Host "════════════════════════════════════" -ForegroundColor Yellow
Write-Host "`n" -ForegroundColor Cyan

Write-Host 'Invoke-WebRequest "http://127.0.0.1:8000/health" | ConvertTo-Json' -ForegroundColor White

# ============================================================================
# MÉTRICAS
# ============================================================================
Write-Host "`n`n" -ForegroundColor White
Write-Host "7️⃣  VER MÉTRICAS EN TIEMPO REAL" -ForegroundColor Yellow
Write-Host "════════════════════════════════" -ForegroundColor Yellow
Write-Host "`n" -ForegroundColor Cyan

Write-Host 'Invoke-WebRequest "http://127.0.0.1:8000/metrics" | ConvertTo-Json' -ForegroundColor White

# ============================================================================
# MODELOS
# ============================================================================
Write-Host "`n`n" -ForegroundColor White
Write-Host "8️⃣  VER MODELOS DISPONIBLES" -ForegroundColor Yellow
Write-Host "═══════════════════════════" -ForegroundColor Yellow
Write-Host "`n" -ForegroundColor Cyan

Write-Host 'Invoke-WebRequest "http://127.0.0.1:8000/models" | ConvertTo-Json' -ForegroundColor White

# ============================================================================
# FUNCIÓN AUXILIAR PARA BÚSQUEDAS
# ============================================================================
Write-Host "`n`n" -ForegroundColor White
Write-Host "9️⃣  CREAR UNA FUNCIÓN REUTILIZABLE" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════" -ForegroundColor Yellow
Write-Host "`nCopia esto una vez y luego puedes usar 'Search-Recipe' en cualquier momento:`n" -ForegroundColor Cyan

$funcionHelper = @'
# Copiar esto en PowerShell
function Search-Recipe {
  param([string]$Query)
  
  $body = @{ query = $Query } | ConvertTo-Json
  $response = Invoke-WebRequest "http://127.0.0.1:8000/recommend" `
    -Method POST -Body $body -ContentType "application/json"
  
  $data = $response.Content | ConvertFrom-Json
  Write-Host "Recetas para: '$Query'" -ForegroundColor Green
  Write-Host "───────────────────────────────────────" -ForegroundColor Green
  
  $data.recetas | ForEach-Object {
    Write-Host "📖 $($_.nombre)" -ForegroundColor Yellow
    Write-Host "   ⭐ Rating: $($_.calificacion_promedio)/5" -ForegroundColor Cyan
    if ($_.tiempo_cocina) {
      Write-Host "   ⏱️  Tiempo: $($_.tiempo_cocina)" -ForegroundColor Cyan
    }
    Write-Host ""
  }
}

# Después puedes usar:
Search-Recipe "pasta con tomate"
Search-Recipe "pollo al horno"
Search-Recipe "postre de chocolate"
'@

Write-Host $funcionHelper -ForegroundColor White

# ============================================================================
# BUCLE PARA BÚSQUEDAS CONTINUAS
# ============================================================================
Write-Host "`n`n" -ForegroundColor White
Write-Host "🔟  BUCLE INTERACTIVO DE BÚSQUEDAS" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════" -ForegroundColor Yellow
Write-Host "`nCopia esto para hacer búsquedas continuas:`n" -ForegroundColor Cyan

$bucle = @'
while ($true) {
  $query = Read-Host "Ingresa tu búsqueda (o 'salir' para terminar)"
  if ($query -eq "salir") { break }
  
  $body = @{ query = $query } | ConvertTo-Json
  try {
    $response = Invoke-WebRequest "http://127.0.0.1:8000/recommend" `
      -Method POST -Body $body -ContentType "application/json"
    
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "`nRecetas para: '$query'" -ForegroundColor Green
    Write-Host "──────────────────────────────" -ForegroundColor Green
    
    $data.recetas | ForEach-Object {
      Write-Host "📖 $($_.nombre) ⭐ $($_.calificacion_promedio)/5" -ForegroundColor Cyan
    }
    Write-Host ""
  }
  catch {
    Write-Host "Error: $_" -ForegroundColor Red
  }
}
'@

Write-Host $bucle -ForegroundColor White

# ============================================================================
# TABLA DE BÚSQUEDAS RECOMENDADAS
# ============================================================================
Write-Host "`n`n" -ForegroundColor White
Write-Host "📊 BÚSQUEDAS RECOMENDADAS PARA PROBAR" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "`n" -ForegroundColor Cyan

$ejemplosQueries = @(
  @{ query = "pasta"; desc = "Búsqueda simple" },
  @{ query = "Pollo al limón"; desc = "Plato específico" },
  @{ query = "Receta vegetariana rápida"; desc = "Dieta + tiempo" },
  @{ query = "Desayuno saludable"; desc = "Comida del día" },
  @{ query = "Postre de chocolate"; desc = "Tipo de postre" },
  @{ query = "Salmón a la mantequilla"; desc = "Plato elegante" },
  @{ query = "Sopa de verduras"; desc = "Comida reconfortante" },
  @{ query = "Pizza casera"; desc = "Comida clásica" },
  @{ query = "Tarta fría"; desc = "Postre sin horno" },
  @{ query = "Ensalada griega"; desc = "Comida ligera" }
)

Write-Host "Copia el query y úsalo en las búsquedas arriba:" -ForegroundColor White
Write-Host ""

foreach ($item in $ejemplosQueries) {
  Write-Host "  Query: " -NoNewline -ForegroundColor Yellow
  Write-Host "$($item.query)" -ForegroundColor White
  Write-Host "  Tipo: $($item.desc)" -ForegroundColor Cyan
  Write-Host ""
}

# ============================================================================
# RESUMEN FINAL
# ============================================================================
Write-Host "`n" -ForegroundColor White
Write-Host "═════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✨ RESUMEN FINAL" -ForegroundColor Green
Write-Host "═════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "`nMétodos para hacer búsquedas:` -ForegroundColor White
Write-Host "  1. 📚 Swagger UI: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "  2. 🔵 PowerShell: Copia los ejemplos de arriba" -ForegroundColor Yellow
Write-Host "  3. 🐍 Python: python ejemplos_busquedas.py" -ForegroundColor Yellow
Write-Host "  4. 🔨 cURL: curl -X POST ... (ver ejemplos en otra sección)" -ForegroundColor Yellow
Write-Host "`n¡Disfruta buscando recetas! 🍽️" -ForegroundColor Green
Write-Host "`n═════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
