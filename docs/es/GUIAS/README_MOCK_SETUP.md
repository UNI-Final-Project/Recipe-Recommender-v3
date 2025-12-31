# 🚀 RESUMEN: Cómo Solucionar Error 429 y Probar Sistema MOCK

## 📋 El Problema

Tu servidor **app.py** intenta usar OpenAI para:
- Crear embeddings (búsquedas semánticas)
- Traducir recetas a español

Pero tu cuenta OpenAI **NO TIENE CRÉDITO** → Error 429

---

## ✅ Solución Inmediata: Modo MOCK

He creado un servidor alternativo que funciona **100% SIN OpenAI**:

### Archivos Creados:

1. **mock_server.py** - Código que simula búsquedas
2. **app_mock.py** - Servidor alternativo sin OpenAI
3. **test_mock_server.py** - Script para probar el servidor
4. **MODO_MOCK_GUIA.md** - Guía completa de uso
5. **SOLUCION_ERROR_429.md** - Soluciones a error 429

---

## 🎯 Pasos Para Probar

### Paso 1: Abrir Terminal en el Directorio del Proyecto

```powershell
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"
```

### Paso 2: Iniciar Servidor MOCK

```powershell
python -m uvicorn app_mock:app --host 127.0.0.1 --port 8000
```

Verás algo como:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**DEJAR ESTA TERMINAL ABIERTA**

### Paso 3: Abrir Segunda Terminal

En otra terminal (en el mismo directorio):

```powershell
python test_mock_server.py
```

Verás pruebas de todos los endpoints con resultados como:
```
✅ Servidor respondiendo
✅ Búsqueda ejecutada - 2 resultados
✅ Todos los tests completados
```

### Paso 4: Probar en Navegador (Visual)

Abre: **http://127.0.0.1:8000/docs**

Verás interfaz Swagger UI donde puedes:
- 🔍 Buscar recetas
- 📊 Ver respuestas JSON
- ✏️ Editar parámetros

---

## 🎭 Qué Hace el Sistema MOCK

### Recetas Simuladas (10 disponibles):
1. Espaguetis Clásicos al Pomodoro
2. Pasta al Pomodoro con Ajo
3. Pasta Cremosa de Tomate
4. Pollo a la Mostaza
5. Salmón al Horno
6. Ensalada Griega
7. Pizza Casera
8. Sopa de Verduras
9. Tarta Fría de Chocolate
10. Tortilla Española

### Palabras Clave que Funcionan:
- `pasta` → retorna 3 recetas de pasta
- `pollo` → retorna receta de pollo
- `salmón` → retorna receta de salmón
- `vegetariano` → retorna recetas sin carne
- `postre` → retorna postres
- `rápida` → retorna recetas rápidas

### Ejemplo de Búsqueda:
```
Query: "pasta"
       ↓
Busca en palabras clave
       ↓
Retorna: Espaguetis, Pasta Pomodoro, Pasta Cremosa
       ↓
JSON con ratings, ingredientes, tiempos
```

---

## 💡 Ejemplos de Uso

### Vía Swagger UI (Recomendado para empezar)
1. Abre: http://127.0.0.1:8000/docs
2. Click en **POST /recommend**
3. Click en **Try it out**
4. Ingresa:
```json
{
  "ingredients": ["tomate", "queso"],
  "num_results": 3
}
```
5. Click **Execute** → Ver respuesta

### Vía PowerShell
```powershell
$body = @{
    query = "pizza"
    num_results = 2
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/recommend" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

### Vía Python
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/recommend",
    json={"query": "sopa", "num_results": 3}
)

print(response.json())
```

---

## 📚 Documentación Completa

| Archivo | Descripción |
|---------|-------------|
| [mock_server.py](mock_server.py) | Código del sistema simulado |
| [app_mock.py](app_mock.py) | Servidor FastAPI sin OpenAI |
| [test_mock_server.py](test_mock_server.py) | Script de pruebas automáticas |
| [MODO_MOCK_GUIA.md](MODO_MOCK_GUIA.md) | Guía completa de uso |
| [SOLUCION_ERROR_429.md](SOLUCION_ERROR_429.md) | Soluciones al error 429 |

---

## 🔄 3 Opciones Para Resolver el Error 429

### Opción 1: Recargar OpenAI (Si tienes presupuesto)
- Ir a: https://platform.openai.com/account/billing/overview
- Agregar crédito o suscripción
- Luego usar: `python -m uvicorn app:app --port 8000`

### Opción 2: Usar MOCK Indefinidamente (Gratis)
- Usar: `python -m uvicorn app_mock:app --port 8000`
- Perfectamente funcional para development/testing
- Sin costo

### Opción 3: Usar Proveedor Alternativo
- Hugging Face (gratis)
- Claude API (pago, pero más barato)
- Ollama (local, gratis)
- Ver [SOLUCION_ERROR_429.md](SOLUCION_ERROR_429.md) para detalles

---

## ⚡ Comandos Rápidos

```powershell
# Cambiar a directorio del proyecto
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"

# Terminal 1: Iniciar servidor MOCK
python -m uvicorn app_mock:app --host 127.0.0.1 --port 8000

# Terminal 2: Probar servidor
python test_mock_server.py

# Luego: Abrir navegador
# http://127.0.0.1:8000/docs

# O probar desde PowerShell
curl -X POST "http://127.0.0.1:8000/recommend" `
  -H "Content-Type: application/json" `
  -d '{"query":"pasta","num_results":3}'
```

---

## 🎓 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | / | Info del servidor |
| GET | /health | Estado (health check) |
| GET | /recetas | Listar todas las recetas |
| GET | /search?q=pasta | Búsqueda simple |
| POST | /recommend | Búsqueda con ingredientes |

---

## ✅ Verificación Final

Después de iniciar `app_mock.py`:

```powershell
# Debe retornar 200 OK
curl -X GET "http://127.0.0.1:8000/"

# Debe mostrar recetas
curl -X POST "http://127.0.0.1:8000/recommend" `
  -H "Content-Type: application/json" `
  -d '{"query":"pasta"}'
```

---

## 📞 Próximos Pasos

### Ahora:
1. ✅ Usa el sistema MOCK para testing
2. ✅ Verifica que todo funciona
3. ✅ Prueba con Swagger UI

### Después:
- 🔴 Si quieres OpenAI: Recarga crédito en platform.openai.com
- 🟢 Si MOCK te funciona: Usa `app_mock.py` en producción
- 🟡 Si quieres alternativa: Sigue guía en SOLUCION_ERROR_429.md

---

**¡El servidor MOCK está listo para usar!** 🎉

Abre: http://127.0.0.1:8000/docs
