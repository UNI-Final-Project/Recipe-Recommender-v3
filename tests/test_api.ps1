# Script para probar los endpoints de la API

Write-Host "=== Probando Endpoints de Recipe Recommender API ===" -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing /health endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Method Get -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "✓ Health Check: OK" -ForegroundColor Green
    Write-Host "  Status: $($content.status)"
} catch {
    Write-Host "✗ Health Check failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 2: Metrics
Write-Host "2. Testing /metrics endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/metrics" -Method Get -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "✓ Metrics retrieved successfully" -ForegroundColor Green
    Write-Host "  Metrics keys: $($content | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name)"
} catch {
    Write-Host "✗ Metrics failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 3: List Models
Write-Host "3. Testing /models endpoint..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/models" -Method Get -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "✓ Models retrieved successfully" -ForegroundColor Green
    Write-Host "  Number of models: $($content.models.Count)"
} catch {
    Write-Host "✗ Models failed: $_" -ForegroundColor Red
}
Write-Host ""

# Test 4: Recommendation API
Write-Host "4. Testing /recommend endpoint..." -ForegroundColor Cyan
try {
    $body = @{
        query = "delicious pasta with tomato"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommend" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    $content = $response.Content | ConvertFrom-Json
    Write-Host "✓ Recommendation API working" -ForegroundColor Green
    Write-Host "  Recipes found: $($content.recetas.Count)"
    if ($content.recetas.Count -gt 0) {
        Write-Host "  First recipe: $($content.recetas[0].nombre)"
    }
} catch {
    Write-Host "✗ Recommendation API failed: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== API Tests Complete ===" -ForegroundColor Green
