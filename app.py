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

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent

# Load .env if present
load_dotenv(PROJECT_ROOT / ".env")

DATA_PKL = os.getenv("DATA_PKL", str(PROJECT_ROOT / "food.pkl"))

# Connect with Qdrant
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_HOST = "https://a48878a9-e5e9-4cf4-9283-4727ea94bd4c.europe-west3-0.gcp.cloud.qdrant.io"

client = QdrantClient(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY
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

    if not Path(DATA_PKL).exists():
        raise FileNotFoundError(f"{DATA_PKL} not found. Place your food.pkl in the project root or set DATA_PKL in .env")
    data = pd.read_pickle(DATA_PKL)

    # Initialize MLflow
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

        # Log model parameters once at startup
        with mlflow.start_run(run_name="model_config"):
            mlflow.log_param("embedding_model", "text-embedding-3-small")
            mlflow.log_param("llm_model", "gpt-4.1-2025-04-14")
            mlflow.log_param("alpha", 0.7)
            mlflow.log_param("n", 3)
            mlflow.log_param("qdrant_collection", "recipes_embeddings_cloud")
            mlflow.log_param("num_recipes", len(data))
            mlflow.end_run()

        print(f"MLflow tracking enabled: {MLFLOW_TRACKING_URI}")
    except Exception as e:
        print(f"MLflow initialization warning: {e}. Tracking may be unavailable.")

# Store OpenAI key
load_dotenv(PROJECT_ROOT / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_api_key = OPENAI_API_KEY

# MLflow Configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "recipe-recommendations")

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
    with mlflow.start_run():
        # Log query info
        try:
            mlflow.log_param("query", q.query[:100])
        except Exception:
            pass  # Silent fail for tracking

        # Track total API latency
        start = time.perf_counter()

        try:
            recs, translation_latency = recommend(q.query)
            validated = RecommendResponse(recetas=recs)

            # Log metrics
            api_latency = (time.perf_counter() - start) * 1000
            try:
                mlflow.log_metric("api_latency_ms", api_latency)
                mlflow.log_metric("translation_latency_ms", translation_latency)
                mlflow.log_metric("num_recipes", len(recs))
                # Save responses
                mlflow.log_text(validated.json(ensure_ascii=False, indent=2), "response.json")
            except Exception:
                pass  # Silent fail for tracking

        except Exception as e:
            try:
                mlflow.log_param("error", str(e)[:200])
            except Exception:
                pass  # Silent fail for tracking
            raise HTTPException(status_code=500, detail=str(e))

    return validated

# To run locally:
# pip install -r requirements.txt
# uvicorn app:app --host 0.0.0.0 --port 8000 --reload
