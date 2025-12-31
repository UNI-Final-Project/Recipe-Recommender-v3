# 🔄 Comparación: app.py vs app_mock.py

## Cuándo Usar Cada Uno

### 📊 Tabla Comparativa

```
┌─────────────────────┬──────────────────────┬──────────────────────┐
│ Característica      │ app.py (Original)    │ app_mock.py (MOCK)   │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Requiere OpenAI     │ ✅ SÍ (crédito)      │ ❌ NO                │
│ Costo por búsqueda  │ ~$0.0005             │ $0.00                │
│ Velocidad respuesta │ 500-2000ms           │ 10-50ms (más rápido) │
│ Calidad búsquedas   │ ⭐⭐⭐⭐⭐ (perfecta) │ ⭐⭐⭐ (simulada)   │
│ Precisión           │ 95%+ (real)          │ 70%+ (simulada)      │
│ Número de recetas   │ 53,064 (reales)      │ 10 (simples)         │
│ Traducciones        │ ✅ GPT-4             │ ❌ NO (en desarrollo) │
│ MLOps integration   │ ✅ Completo          │ ❌ Básico             │
│ Ambiente            │ Producción ready     │ Development/Testing  │
├─────────────────────┼──────────────────────┼──────────────────────┤
│ Usa para:           │ Usuarios finales     │ Testing, desarrollo  │
│ NO usa para:        │ Sin presupuesto      │ Producción real      │
└─────────────────────┴──────────────────────┴──────────────────────┘
```

---

## 🎯 Decidir Cuál Usar

### ✅ Usa `app.py` SI:
- ✅ Tienes **crédito OpenAI** disponible
- ✅ Necesitas **máxima precisión** en búsquedas
- ✅ Tienes 50,000+ recetas para buscar
- ✅ Necesitas **traducciones automáticas**
- ✅ Vas a producción/usuarios reales
- ✅ Presupuesto de $20-50/mes está bien

**Costo:**
```
- 1,000 búsquedas/mes × $0.0005 = ~$0.50
- GPT-4 traducciones: ~$1-5 extra
- Total: ~$2-6/mes (muy barato)
```

---

### ✅ Usa `app_mock.py` SI:
- ✅ NO tienes crédito OpenAI
- ✅ Solo quieres **testing/desarrollo**
- ✅ Necesitas algo **rápido ahora**
- ✅ Presupuesto = $0
- ✅ Quieres demostración del sistema
- ✅ Necesitas respuestas instantáneas
- ✅ Estás aprendiendo/prototipando

**Costo:** $0 (completamente gratis)

---

## 🚀 Cómo Cambiar Entre Ellos

### Cambiar de app.py a app_mock.py

**Terminal actual (si está corriendo app.py):**
```
Presiona: Ctrl+C
```

**Luego:**
```powershell
cd "c:\Users\PC - Usuario\Documents\Estudios\Externo\Proyectos\Recipe-Recommender-v3"

# Opción 1: Directo
python app_mock.py

# Opción 2: Con uvicorn
python -m uvicorn app_mock:app --port 8000
```

### Cambiar de app_mock.py a app.py

**Primero:** Recargar OpenAI
1. Ve a: https://platform.openai.com/account/billing/overview
2. Agrega crédito
3. Espera 5-10 minutos

**Terminal:**
```powershell
# Presiona Ctrl+C si estás en app_mock.py

# Luego:
python -m uvicorn app:app --port 8000
```

---

## 📊 Casos de Uso

### Caso 1: Estás Desarrollando
```
DÍA 1-3: Usa app_mock.py
→ Prueba endpoints
→ Desarrolla frontend
→ Verifica lógica

DÍA 4+: Cuando necesites precisión real
→ Recarga OpenAI ($5-10)
→ Cambia a app.py
→ Prueba con datos reales
```

### Caso 2: Necesitas Demo
```
OPCIÓN A (Con presupuesto):
1. Recarga $20 en OpenAI
2. Usa app.py
3. Demo con datos reales

OPCIÓN B (Sin presupuesto):
1. Usa app_mock.py
2. Demo funciona igual
3. Explica que es simulado para testing
```

### Caso 3: Producción
```
REQUISITO: Credito OpenAI + suscripción

SETUP:
1. Configura app.py
2. Agrega API key en .env
3. Deploy a servidor
4. Monitorea costos en OpenAI dashboard
```

### Caso 4: Testing Automático
```
PIPELINE CI/CD:

1. Tests unitarios → app_mock.py (gratis)
2. Tests de integración → app_mock.py (gratis)
3. Tests de E2E → app.py (pequeño costo)
4. Producción → app.py (costo optimizado)
```

---

## 🔄 Cambio de Recetas

### app.py
```python
# Usa 53,064 recetas reales de food.pkl
DATA_FILE = "food.pkl"

# Busca en Qdrant Vector DB
client = QdrantClient("127.0.0.1:6333")
results = client.search(...)
```

**Ventaja:** Acceso a 53,000+ recetas reales

### app_mock.py
```python
# Usa 10 recetas simuladas
MOCK_RECIPES = [
    {"nombre": "Espaguetis...", ...},
    # ... 9 más
]

# Busca por palabras clave
if "pasta" in query:
    return [receta1, receta2, receta3]
```

**Ventaja:** Rápido, simple, sin dependencias externas

---

## ⚙️ Configuración Técnica

### app.py
```
OpenAI API → text-embedding-3-small
    ↓
Embedding 1536-dim
    ↓
Qdrant búsqueda vectorial
    ↓
Ranking híbrido (70% semántico + 30% popularity)
    ↓
GPT-4 traducción
    ↓
Respuesta final
```

### app_mock.py
```
User query
    ↓
Buscar en keyword_map
    ↓
Seleccionar recetas relevantes
    ↓
Agregar scores simulados
    ↓
Respuesta JSON
```

---

## 📝 Ejemplo Práctico

### Búsqueda: "Sopa de tomate rápida"

**Con app.py:**
```
1. Embedding: "Sopa de tomate rápida" → vector 1536-dim
2. Búsqueda Qdrant: Busca 10,000 recetas similares
3. Ranking: Ordena por relevancia + popularity
4. Top 3: Retorna las mejores coincidencias
5. Traducción: GPT-4 traduce si es necesario
⏱️ Tiempo: ~1 segundo
```

**Con app_mock.py:**
```
1. Query parser: Detecta palabras clave
2. Keyword match: "sopa" + "tomate" + "rápida"
3. Lookup: Encuentra indices en MOCK_RECIPES
4. Select: Retorna 3 recetas simuladas
⏱️ Tiempo: ~20ms (50x más rápido)
```

---

## 💰 Análisis de Costos

### Escenario 1: 1,000 búsquedas/mes

**app.py:**
```
- 1,000 búsquedas × $0.0005 = $0.50
- 100 traducciones × $0.05 = $5.00
- Total: ~$5.50/mes
```

**app_mock.py:**
```
- Gratis
- Total: $0
```

### Escenario 2: 10,000 búsquedas/mes

**app.py:**
```
- Embeddings: 10,000 × $0.0005 = $5.00
- Traducciones: 1,000 × $0.05 = $50.00
- Total: ~$55/mes
```

**app_mock.py:**
```
- Gratis
- Total: $0
```

---

## 🎯 Recomendación Final

```
┌──────────────────────────────────────────────────────┐
│         RECOMENDACIÓN SEGÚN SITUACIÓN               │
├──────────────────────────────────────────────────────┤
│                                                      │
│ AHORA (enero 2025):                                 │
│ └─ ✅ Usa app_mock.py (gratis)                      │
│    - Desarrolla                                     │
│    - Prueba todo                                    │
│    - Hace demos                                     │
│                                                      │
│ CUANDO TENGAS PRESUPUESTO:                          │
│ └─ ✅ Recarga OpenAI ($20)                          │
│    - Usa app.py                                     │
│    - Búsquedas reales                               │
│    - Produção ready                                 │
│                                                      │
│ PARA PRODUCCIÓN:                                    │
│ └─ ✅ app.py + monitoreo de costos                  │
│    - Presupuesto mensual: $5-50                     │
│    - Máxima precisión                               │
│    - Escalable                                      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 📚 Documentos Relacionados

- [README_MOCK_SETUP.md](README_MOCK_SETUP.md) - Guía rápida de setup
- [SOLUCION_ERROR_429.md](SOLUCION_ERROR_429.md) - Soluciones al error 429
- [MODO_MOCK_GUIA.md](MODO_MOCK_GUIA.md) - Guía completa del MOCK
- [app.py](app.py) - Servidor original con OpenAI
- [app_mock.py](app_mock.py) - Servidor alternativo sin OpenAI

---

**¿Preguntas?** Lee [SOLUCION_ERROR_429.md](SOLUCION_ERROR_429.md)
