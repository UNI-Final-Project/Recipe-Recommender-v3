from pathlib import Path
import os
import json
import pickle
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import numpy as np
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import mlflow

# MLOps imports
from mlops import (
    config,
    app_logger,
    mlops_logger,
    monitoring_logger,
    model_registry,
    metrics_collector,
    anomaly_detector,
    health_monitor,
    auto_scheduler,
)

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env if present
load_dotenv(PROJECT_ROOT / "config" / ".env")

DATA_PKL = os.getenv("DATA_PKL", str(PROJECT_ROOT / "food.pkl"))

# MLflow Configuration - MUST BE BEFORE @app.on_event
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", str(PROJECT_ROOT / "mlruns"))
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "recipe-recommendations")

# Store OpenAI key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_api_key = OPENAI_API_KEY

# Connect with Qdrant
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_HOST = "https://a48878a9-e5e9-4cf4-9283-4727ea94bd4c.europe-west3-0.gcp.cloud.qdrant.io"

client = QdrantClient(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY,
    check_compatibility=False  # Suppress version check warning
)

app = FastAPI(title="Simple Recipes Recommender API")

class QueryIn(BaseModel):
    query: str

class RecipeOut(BaseModel):
    nombre: str
    descripción: str
    ingredientes: List[str]
    instrucciones: List[str]
    calificación_promedio: float

    @field_validator("ingredientes", mode="before")
    def parse_ingredientes_list(cls, v):
        if isinstance(v, str):
            v = v.strip("[]").replace("'", "").replace('"', "")
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @field_validator("instrucciones", mode="before")
    def parse_instrucciones_list(cls, v):
        if isinstance(v, str):
            v = v.strip("[]").replace("'", "").replace('"', "")
            return [i.strip() for i in v.split(",") if i.strip()]
        return v


class RecommendResponse(BaseModel):
    recetas: List[RecipeOut]

# Global placeholders
data = None
text_emb = None
embedder = None
scaled_features = None
feature_cols = []

@app.on_event("startup")
def load_resources():
    global data, text_emb, embedder, scaled_features, feature_cols

    try:
        if not Path(DATA_PKL).exists():
            raise FileNotFoundError(f"{DATA_PKL} not found. Place your food.pkl in the project root or set DATA_PKL in .env")
        data = pd.read_pickle(DATA_PKL)
        
        app_logger.info(f"Data loaded: {len(data)} recipes")

        # Initialize and configure MLflow
        try:
            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
            
            # Registrar configuración inicial del modelo
            with mlflow.start_run(run_name="startup_config"):
                mlflow.log_params({
                    "embedding_model": "text-embedding-3-small",
                    "llm_model": "gpt-4.1-2025-04-14",
                    "alpha": 0.7,
                    "n": 3,
                    "qdrant_collection": "recipes_embeddings_cloud",
                    "num_recipes": len(data),
                })
            
            # Registrar modelo de producción actual
            from mlops.model_registry import ModelMetadata
            
            prod_model = model_registry.get_production_model("hybrid_ranker")
            if not prod_model:
                # Registrar como modelo inicial
                metadata = ModelMetadata(
                    model_id="hybrid_ranker",
                    model_type="hybrid",
                    version="1.0.0",
                    description="Initial production model - Hybrid semantic + popularity ranker",
                    metrics={
                        "alpha": 0.7,
                        "status": "production"
                    },
                    parameters={
                        "embedding_model": "text-embedding-3-small",
                        "llm_model": "gpt-4.1-2025-04-14",
                        "ranking_algorithm": "hybrid",
                        "features": ["semantic_score", "popularity_score"]
                    },
                    status="production",
                    tags={
                        "environment": "production",
                        "initial_version": "true"
                    }
                )
                model_registry.register_model(metadata)
                app_logger.info("Initial model registered in production")
            
            app_logger.info(f"MLflow tracking enabled: {MLFLOW_TRACKING_URI}")
            mlops_logger.info(f"MLOps system initialized successfully")
            
        except Exception as e:
            app_logger.warning(f"MLflow/MLOps initialization warning: {e}")
            mlops_logger.warning(f"MLOps tracking may be unavailable: {e}")
    
    except FileNotFoundError as e:
        app_logger.error(f"Startup error: {e}")
        raise
    except Exception as e:
        app_logger.error(f"Unexpected startup error: {e}")
        raise

def recommend_for_new_user(query, n=3, alpha=0.7, return_scores=False, openai_api_key=openai_api_key, client=client):
    # Generate embedding for the query
    openai_client = OpenAI(api_key=openai_api_key)
    query_embedding = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding
    
    # Query Qdrant for semantic similarity
    search_result = client.query_points(
        collection_name="recipes_embeddings_cloud", 
        query=query_embedding, 
        limit=n*2  # Get more to re-rank
    ).points
    
    # Extract IDs and scores
    ids = [point.id for point in search_result]
    semantic_scores = np.array([point.score for point in search_result])
    
    # Popularity scores (normalized)
    pop_score = data["average_rating"].fillna(data["average_rating"].mean()).to_numpy()
    pop_score = pop_score / pop_score.max()
    
    # Hybrid score: alpha for semantic, (1-alpha) for popularity
    hybrid_scores = alpha * semantic_scores + (1 - alpha) * pop_score[ids]
    
    # Get top n based on hybrid score
    top_indices = np.argsort(hybrid_scores)[::-1][:n]
    top_ids = [ids[i] for i in top_indices]
    
    # Convert the rating to two decimals
    data["average_rating"] = data["average_rating"].round(2)
    
    # Output the name, description, ingredients and rating
    result = data.iloc[top_ids][["name", "average_rating", "description", "ingredients", "steps"]].copy()
    
    # Rearrange columns and rename
    result = result[["name", "description", "ingredients", "steps", "average_rating"]]
    result = result.rename(columns={
        'name': 'nombre', 
        'description': 'descripción', 
        'ingredients': 'ingredientes', 
        'average_rating': 'calificación_promedio', 
        'steps': 'instrucciones'
    })
    
    if return_scores:
        result['hybrid_score'] = hybrid_scores[top_indices]
    
    return result.reset_index(drop=True)

# Initialize LLM.
llm = ChatOpenAI(model="gpt-4.1-2025-04-14", api_key=openai_api_key)

# Prompts to translate
translate_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant that translates the name, description, ingredients, instructions, and average_rating of food recipes into Spanish. Respect the JSON format strictly. Also, ensure that you organize the recipe's instructions step by step in numeric bullets. Do not include any comments about your chain of thought."),
    ("user", "Translate the following recipe:\n{var1}")
])

detect_language_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an assistant that detects the language of a given text. If the text is in English, return the exact text without any modifications or additional commentary. If the text is in any other language, translate it to English and return only the translated text in a straightforward manner. Do not include any comments about your chain of thought."),
    ("user", "Detect the language of the following text:\n{query}")
])

# Chains
translate_chain = translate_prompt | llm | StrOutputParser()
detect_language_chain = detect_language_prompt | llm | StrOutputParser()

# translate to spanish + summarize
def recommend(query, n=3, alpha=0.7, return_scores=False):
    # Detect language and translate to English if necessary
    query = detect_language_chain.invoke({"query": query})
    # Get recommendations
    recommendations = recommend_for_new_user(query, n, alpha, return_scores)
    # Transform to JSON structure
    recommendations_json = recommendations.to_dict(orient="records")
    # Apply LLM chain
    translated_recipes = []

    # Track translation time
    translation_start = time.perf_counter()

    for recipe in recommendations_json:
        translated_json = translate_chain.invoke({"var1": json.dumps(recipe, ensure_ascii=False)})
        translated_dict = json.loads(translated_json)  # parsear a dict
        translated_recipes.append(translated_dict)

    translation_latency = (time.perf_counter() - translation_start) * 1000

    return translated_recipes, translation_latency

@app.post("/recommend")
def recommend_endpoint(q: QueryIn):
    """
    Endpoint de recomendación con monitoreo y logging completo
    """
    request_id = f"{time.time_ns()}"
    start_time = time.perf_counter()
    
    try:
        # Log de solicitud
        app_logger.info(f"Recommendation request received", extra={
            "request_id": request_id,
            "query": q.query[:100]
        })
        
        with mlflow.start_run(run_name=f"recommend_{request_id}"):
            # Log de parámetros
            mlflow.log_param("request_id", request_id)
            mlflow.log_param("query_length", len(q.query))
            
            try:
                # Obtener recomendaciones
                recs, translation_latency = recommend(q.query)
                validated = RecommendResponse(recetas=recs)
                
                # Calcular métricas
                total_latency = (time.perf_counter() - start_time) * 1000
                api_latency = total_latency - translation_latency
                
                # Registrar métricas en el collector
                metrics_collector.record("api_latency_ms", api_latency)
                metrics_collector.record("translation_latency_ms", translation_latency)
                metrics_collector.record("num_recipes", len(recs))
                metrics_collector.record("request_count", 1)
                
                # Log en MLflow
                mlflow.log_metric("api_latency_ms", api_latency)
                mlflow.log_metric("translation_latency_ms", translation_latency)
                mlflow.log_metric("total_latency_ms", total_latency)
                mlflow.log_metric("num_recipes", len(recs))
                mlflow.log_text(validated.model_dump_json(indent=2), "response.json")
                
                # Log de éxito
                app_logger.info(f"Recommendation successful", extra={
                    "request_id": request_id,
                    "latency_ms": total_latency,
                    "recipes_returned": len(recs)
                })
                
                # Verificar anomalías
                if api_latency > config.alert_threshold_latency:
                    monitoring_logger.warning(
                        f"High latency detected",
                        extra={
                            "request_id": request_id,
                            "latency_ms": api_latency,
                            "threshold_ms": config.alert_threshold_latency
                        }
                    )
                
                return validated
            
            except Exception as e:
                mlflow.log_param("error_type", type(e).__name__)
                mlflow.log_param("error_message", str(e)[:200])
                
                app_logger.error(f"Error during recommendation", extra={
                    "request_id": request_id,
                    "error": str(e)
                })
                
                metrics_collector.record("error_rate", 1)
                
                raise HTTPException(status_code=500, detail=str(e))
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Unexpected error", extra={
            "request_id": request_id,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="Unexpected error")

@app.get("/")
def root():
    """
    Endpoint raíz - Redirecciona a documentación
    """
    return {
        "message": "Recipe Recommender API - MLOps Edition",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "recommend": "/recommend",
            "metrics": "/metrics",
            "models": "/models"
        }
    }

@app.get("/health")
def health_check():
    """
    Endpoint de salud del sistema
    """
    try:
        import sys
        return {
            "status": "healthy",
            "timestamp": pd.Timestamp.now().isoformat(),
            "service": "Recipe Recommender API",
            "version": "1.0.0",
            "data_loaded": data is not None,
            "num_recipes": len(data) if data is not None else 0,
            "model_production": "hybrid_ranker v1.0.0"
        }
    except Exception as e:
        app_logger.error(f"Health check error: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": pd.Timestamp.now().isoformat(),
            "error": str(e)
        }

@app.get("/metrics")
def get_metrics(window_minutes: int = 60):
    """
    Obtiene métricas de los últimos N minutos
    """
    metrics_summary = {
        "timestamp": time.time(),
        "window_minutes": window_minutes,
        "metrics": {}
    }
    
    metric_names = ["api_latency_ms", "translation_latency_ms", "error_rate", "num_recipes"]
    for metric_name in metric_names:
        stats = metrics_collector.get_stats(metric_name, window_minutes=window_minutes)
        if stats:
            metrics_summary["metrics"][metric_name] = stats
    
    return metrics_summary

@app.get("/models")
def list_models():
    """
    Lista todos los modelos registrados
    """
    models = model_registry.list_models()
    return {
        "count": len(models),
        "models": models
    }

@app.get("/models/{model_id}/production")
def get_production_model(model_id: str):
    """
    Obtiene el modelo en producción para un modelo_id
    """
    prod_model = model_registry.get_production_model(model_id)
    if not prod_model:
        raise HTTPException(status_code=404, detail=f"No production model found for {model_id}")
    return prod_model

@app.post("/retrain/check")
def check_retrain_needed():
    """
    Verifica si hay modelos que necesiten retraining
    """
    model_ids = ["hybrid_ranker"]  # Modelos a monitorear
    results = auto_scheduler.check_and_schedule_retraining(model_ids)
    return results

# To run locally:
# pip install -r requirements.txt
# uvicorn app:app --host 0.0.0.0 --port 8000 --reload
