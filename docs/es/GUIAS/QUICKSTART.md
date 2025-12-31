# 🚀 Quick Installation Guide

## Step 1: Clone and Setup

```bash
# Navigate to project directory
cd Recipe-Recommender-v3

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import mlops; print('✓ MLOps module loaded')"
```

## Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Required:
# - OPENAI_API_KEY
# - QDRANT_API_KEY
# - QDRANT_HOST
```

## Step 4: Start Services

### Terminal 1: Start API
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Start MLflow UI
```bash
mlflow ui --backend-store-uri ./mlruns
```

## Step 5: Verify Installation

### Check API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "timestamp": "2024-12-30T...",
  "overall_status": "healthy",
  "api": {...},
  "checks": {...}
}
```

### Check MLflow UI
```
Open browser: http://localhost:5000
```

You should see MLflow experiments dashboard.

### Test Recommendation Endpoint
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "recetas con pollo"}'
```

## Step 6: Run Tests (Optional)

```bash
# Run all MLOps tests
python test_mlops.py

# Or run specific tests
python -m unittest test_mlops.TestModelRegistry -v
```

---

## 📊 Verify Installation

After completing above steps, you should have:

```
✅ API running on http://localhost:8000
✅ MLflow UI on http://localhost:5000
✅ Logs directory created: ./logs/
✅ Models registry created: ./models/registry.json
✅ MLflow runs directory: ./mlruns/
```

---

## 🔍 Quick Sanity Checks

### 1. Check API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# List models
curl http://localhost:8000/models

# Get metrics
curl http://localhost:8000/metrics

# Check retraining
curl -X POST http://localhost:8000/retrain/check
```

### 2. Check Logs
```bash
# View application logs
tail -f logs/app_*.log | jq '.'

# View MLOps logs
tail -f logs/mlops_*.log | jq '.'

# View monitoring logs
tail -f logs/monitoring_*.log | jq '.'
```

### 3. Check MLflow
```bash
# List experiments
mlflow experiments list

# List runs
mlflow runs list
```

---

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError: No module named 'mlops'

**Solution:**
```bash
# Ensure you're in project root
cd /path/to/Recipe-Recommender-v3

# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run with python directly
python -c "import mlops; print('✓ OK')"
```

### Issue: Permission denied for logs directory

**Solution:**
```bash
# Fix permissions
chmod 755 logs/
chmod 755 mlops/
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use different port
uvicorn app:app --port 8001

# Or kill process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

### Issue: OpenAI/Qdrant connection fails

**Solution:**
```bash
# Verify environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print(f'OPENAI_API_KEY: {os.getenv(\"OPENAI_API_KEY\")[:10]}...')
print(f'QDRANT_API_KEY: {os.getenv(\"QDRANT_API_KEY\")[:10]}...')
"

# Check .env file exists and has values
cat .env
```

---

## 📈 Next Steps

After successful installation:

1. **Try the API**
   ```bash
   curl -X POST http://localhost:8000/recommend \
     -H "Content-Type: application/json" \
     -d '{"query": "pasta carbonara"}'
   ```

2. **Monitor in Real-time**
   - Open http://localhost:5000 (MLflow)
   - Open http://localhost:8000/docs (FastAPI docs)

3. **Check Metrics**
   ```bash
   curl http://localhost:8000/metrics?window_minutes=60 | jq '.'
   ```

4. **Test Retraining**
   ```bash
   python schedule_retraining.py
   ```

5. **Read Documentation**
   - Start with `README.md`
   - Deep dive: `MLOPS_GUIDE.md`
   - Check: `CHECKLIST.md`

---

## 📚 Documentation Structure

- **README.md** - Overview and features (start here!)
- **MLOPS_GUIDE.md** - Comprehensive guide (400+ lines)
- **MLOPS_IMPLEMENTATION.md** - What was implemented
- **VISUAL_SUMMARY.md** - Architecture diagrams
- **CHECKLIST.md** - Validation checklist
- This file - Quick installation

---

## ✅ Verification Checklist

After installation, verify:

- [ ] Dependencies installed (`pip list`)
- [ ] .env file created with credentials
- [ ] API running on port 8000
- [ ] MLflow UI on port 5000
- [ ] `/health` endpoint returns 200
- [ ] `/models` endpoint returns models list
- [ ] Logs directory created
- [ ] Models registry.json created
- [ ] Tests pass (`python test_mlops.py`)
- [ ] Can make recommendation request

---

## 🎯 Success Indicators

Installation is successful when:

```
✅ API responds to requests
✅ MLflow UI is accessible
✅ Logs are being created
✅ Metrics are being collected
✅ Models are being tracked
✅ No errors in console
✅ All tests pass
```

---

## 💡 Tips & Tricks

### View API Documentation
```
Open: http://localhost:8000/docs
```

### Stream Logs with Formatting
```bash
# Pretty print JSON logs
tail -f logs/app_*.log | jq '.'

# Filter by level
grep ERROR logs/mlops_*.log | jq '.'

# Filter by timestamp
grep "2024-12" logs/app_*.log | jq '.'
```

### Query MLflow Data
```bash
# List all runs
mlflow runs list --experiment-id 0

# Get specific run
mlflow runs describe --run-id <run-id>

# Compare runs
mlflow runs compare --run-ids <id1> <id2>
```

### Monitor System Health
```bash
# Watch health in real-time
watch curl http://localhost:8000/health

# Or with jq
watch 'curl -s http://localhost:8000/health | jq .overall_status'
```

---

## 📞 Getting Help

If you encounter issues:

1. Check **CHECKLIST.md** - Common issues listed
2. Review **MLOPS_GUIDE.md** - Detailed documentation
3. Check logs in `./logs/` directory
4. Run tests: `python test_mlops.py`
5. Verify `.env` file is correct

---

## 🎉 You're Ready!

Your MLOps-enabled Recipe Recommender is now ready to use!

Start with the API and explore the monitoring capabilities.

---

**Installation verified: ✅**
**Ready for production: ✅**
**Questions? See: README.md and MLOPS_GUIDE.md**
