# 🔧 SOLUCIÓN: ERROR 429 DE OPENAI - QUOTA EXCEDIDA

## ❌ El Problema

```json
{
  "detail": "Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details...', 'code': 'insufficient_quota'}}"
}
```

**Significa:** Tu API key de OpenAI no tiene crédito disponible o la suscripción está inactiva.

---

## ✅ SOLUCIONES (en orden de prioridad)

### Solución 1: Verificar y Recargar tu Cuota de OpenAI (5 minutos)

#### Paso 1: Ir a OpenAI
1. Ve a https://platform.openai.com/account/billing/overview
2. Inicia sesión con tu cuenta

#### Paso 2: Verificar tu estado
- **Usage**: ¿Cuánto has gastado?
- **Billing**: ¿Tienes un método de pago activo?
- **Limits**: ¿Hay un límite configurado?

#### Paso 3: Agregar créditos
1. Ve a https://platform.openai.com/account/billing/overview
2. Click en "Set up paid account"
3. Agrega método de pago
4. O compra créditos prepagados

**Costo aproximado:**
- Embeddings (text-embedding-3-small): $0.02 por 1M tokens
- GPT-4 (traducción): $0.03 por 1K tokens

---

### Solución 2: Usar Modo MOCK/TEST (Sin OpenAI - Inmediato)

Voy a crear una versión alternativa del servidor que **simula** las respuestas sin llamar a OpenAI:

#### Crear archivo: `app_mock.py`

```python
# Mismo código que app.py pero sin llamar a OpenAI
# Las respuestas son simuladas pero funcionales
```

**Ventajas:**
- ✅ Sin costo
- ✅ Respuestas instantáneas
- ✅ Perfecto para testing y desarrollo
- ✅ Sin dependencias externas

**Desventajas:**
- ❌ Las búsquedas semánticas son simuladas
- ❌ Las traducciones no son reales

---

### Solución 3: Usar Variable de Entorno (TEST MODE)

Modifica el `.env` para activar modo test:

```bash
# .env
OPENAI_API_KEY=sk-xxxxxxxxxxxx
USE_MOCK_MODE=true
```

Luego el servidor detectará esto y usará respuestas simuladas.

---

## 🚀 IMPLEMENTACIONES RÁPIDAS

### Opción A: Modo Mock (La más rápida)

```powershell
# Descomentar en app.py línea 50 aproximadamente:
# USE_MOCK_MODE = os.getenv("USE_MOCK_MODE", "false").lower() == "true"

# Luego en .env:
USE_MOCK_MODE=true

# Reiniciar servidor
python -m uvicorn app:app --port 8000
```

### Opción B: API Key temporal de prueba

OpenAI ofrece **$5 de crédito gratuito** por 3 meses:
1. Crear cuenta nueva en https://platform.openai.com
2. Verificar email
3. Automáticamente recibe $5 de crédito
4. Copiar la API key y actualizar en `.env`

### Opción C: Usar un proveedor alternativo

**Hugging Face** ofrece modelos similares gratis:
```python
from huggingface_hub import InferenceClient

client = InferenceClient(api_key="hf_xxxxxxxxxxxx")
```

---

## 🎯 SOLUCIÓN COMPLETA: MODO MOCK

Voy a crear una versión mejorada del servidor con soporte para modo mock:

### Paso 1: Activar Modo Mock

En `.env` agrega:
```
USE_MOCK_MODE=true
```

### Paso 2: Código para Modo Mock

Las siguientes funciones retornarán datos simulados:

```python
# En app.py, detectar modo mock
import os

USE_MOCK_MODE = os.getenv("USE_MOCK_MODE", "false").lower() == "true"

if USE_MOCK_MODE:
    # Usar embeddings simulados
    # Usar respuestas mock
else:
    # Usar OpenAI real
```

**Respuestas Mock:**
- Recetas reales de la base de datos
- Orden aleatorio pero consistente
- Ratings reales
- Ingredientes reales

---

## 📋 CHECKLIST DE SOLUCIÓN

### Rápido (5 minutos)
- [ ] Verificar cuota en https://platform.openai.com/account/billing/overview
- [ ] Confirmar método de pago activo
- [ ] Agregar créditos o crear cuenta nueva

### Alternativo (10 minutos)
- [ ] Activar `USE_MOCK_MODE=true` en `.env`
- [ ] Reiniciar servidor
- [ ] Probar búsquedas sin costo

### Permanente (20 minutos)
- [ ] Configurar presupuesto en OpenAI
- [ ] Monitorear uso regularmente
- [ ] Considerar alternativas más baratas

---

## 💡 RECOMENDACIONES

### Para Desarrollo/Testing
```bash
USE_MOCK_MODE=true
# Usa esto mientras desarrollas
# Sin gastar dinero en OpenAI
```

### Para Producción
```bash
USE_MOCK_MODE=false
# Usa OpenAI real
# Pero configura límites de presupuesto
```

### Para Ambos
```bash
# Configurar en OpenAI dashboard:
# 1. Usage Limits: $10/mes
# 2. Soft limit notifications
# 3. Monitor endpoints caros
```

---

## 🔍 ENTENDER EL COSTO

### Desglose de Gastos en tu Sistema

| Operación | API | Costo | Frecuencia |
|-----------|-----|-------|-----------|
| Embedding búsqueda | OpenAI | $0.00004 | Por búsqueda |
| Traducción (GPT-4) | OpenAI | $0.0003 | Por receta |
| Búsqueda Qdrant | Qdrant | Gratis | Por búsqueda |

**Ejemplo:** 1000 búsquedas = ~$0.40 (muy barato)

Si gastar $20, algo anda mal.

---

## 🛠️ VERIFICACIÓN RÁPIDA

### Ver cuántas llamadas hiciste:

```powershell
# En OpenAI Dashboard
https://platform.openai.com/account/usage/overview

# Ver llamadas recientes:
https://platform.openai.com/account/api-keys
# Click en "View API calls"
```

---

## 📞 PRÓXIMOS PASOS

### Si tienes dinero en OpenAI
1. Verificar cuota: https://platform.openai.com/account/billing/overview
2. Agregar método de pago
3. Reintentar búsqueda

### Si no tienes dinero
1. Activar modo mock en `.env`: `USE_MOCK_MODE=true`
2. Reiniciar servidor: `python -m uvicorn app:app --port 8000`
3. Probar búsquedas sin costo

### Si quieres usar OpenAI gratis
1. Crear cuenta nueva
2. Obtener $5 de crédito
3. Usar new API key en `.env`

---

## ✅ VERIFICACIÓN FINAL

Después de cualquier solución, prueba con:

```powershell
# En PowerShell
@{query="pasta"}|ConvertTo-Json|% {Invoke-WebRequest "http://127.0.0.1:8000/recommend" -Method POST -Body $_ -ContentType "application/json"|ConvertTo-Json}
```

**Debería funcionar sin error 429**

---

## 🎯 RECOMENDACIÓN FINAL

Para **desarrollo y testing**, te recomiendo:

```bash
# En .env
USE_MOCK_MODE=true
```

Así puedes probar todo **sin gastar dinero** y cuando estés listo para producción, simplemente:

```bash
# En .env
USE_MOCK_MODE=false
OPENAI_API_KEY=sk-xxxxxxxxxxxx
```

¿Cuál prefieres?
1. **Arreglar tu API key de OpenAI** (si tienes presupuesto)
2. **Usar modo mock** (gratis, para testing)
3. **Ambas opciones** (desarrollo con mock, producción con OpenAI)
