from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import os
import json
import pickle
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent

# Load .env if present
load_dotenv(PROJECT_ROOT / ".env")

DATA_PKL = os.getenv("DATA_PKL", str(PROJECT_ROOT / "food.pkl"))
TEXT_EMB_PKL = os.getenv("TEXT_EMB_PKL", str(PROJECT_ROOT / "text_emb.pkl"))
EMBEDDER_PKL = os.getenv("EMBEDDER_PKL", str(PROJECT_ROOT / "tfidf_vectorizer.pkl"))

app = FastAPI(title="Simple Recipes Recommender API")

class QueryIn(BaseModel):
    query: str

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

    if not Path(TEXT_EMB_PKL).exists() or not Path(EMBEDDER_PKL).exists():
        raise FileNotFoundError("Embeddings or embedder pickle not found. Generate them in the notebook and place them in the project root.")

    with open(TEXT_EMB_PKL, "rb") as f:
        text_emb = pickle.load(f)
    with open(EMBEDDER_PKL, "rb") as f:
        embedder = pickle.load(f)

    # minimal feature columns; adjust if your dataset differs
    feature_cols = [c for c in [
    'minutes', 'n_steps', 'calories', 'protein', 'total_fat', 'sodium', 'saturated_fat',
      'carbohydrates', 'dairy-free', 'gluten-free', 'healthy', 'fast-cooking', 'vegetarian', 'vegan', 'large-portion', 'low-saturated-fat'
    ] if c in data.columns]

    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(data[feature_cols].fillna(0))

def recommend_for_new_user(query, n=3, alpha=0.6, beta=0.3, return_scores=False):
    # Embed the query
    query_emb = embedder.transform([query])

    # Semantic similarity
    sim_text = cosine_similarity(query_emb, text_emb).flatten()

    # Numeric feature similarity
    sim_features = scaled_features.mean(axis=1)

    # Popularity
    pop_score = data["average_rating"].fillna(data["average_rating"].mean()).to_numpy()
    pop_score = pop_score / pop_score.max()

    # Score final
    hybrid_score = alpha * sim_text + beta * sim_features + (1 - alpha - beta) * pop_score
    top_idx = np.argsort(hybrid_score)[::-1][:n]

    # Convert the rating to two decimals
    data["average_rating"] = data["average_rating"].round(2)

    # Output the name, description, ingredients and rating in that order
    result = data.iloc[top_idx][["name", "average_rating", "description", "ingredients", "steps"]].copy()

    # Rearrange columns and rename
    result = result[["name", "description", "ingredients", "steps", "average_rating"]]
    result = result.rename(columns={'name': 'nombre', 'description': 'descripción', 'ingredients': 'ingredientes', 'average_rating': 'calificación_promedio', 'steps': 'instrucciones'})

    return result.reset_index(drop=True)

# Store OpenAI key
load_dotenv(PROJECT_ROOT / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize LLM
llm = ChatOpenAI(model="gpt-4.1-2025-04-14")

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
def recommend(query, n=3, alpha=0.6, beta=0.3, return_scores=False):
    # Detect language and translate to English if necessary
    query = detect_language_chain.invoke({"query": query})
    # Get recommendations
    recommendations = recommend_for_new_user(query, n, alpha, beta, return_scores)
    # Transform to JSON structure
    recommendations_json = recommendations.to_dict(orient="records")
    # Apply LLM chain
    translated_recipes = []

    for recipe in recommendations_json:
        translated_json = translate_chain.invoke({"var1": json.dumps(recipe, ensure_ascii=False)})
        translated_dict = json.loads(translated_json)  # parsear a dict
        translated_recipes.append(translated_dict)

    return translated_recipes

@app.post("/recommend")
def recommend_endpoint(q: QueryIn):
    try:
        recs = recommend(q.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return recs

# To run locally:
# pip install -r requirements.txt
# uvicorn app:app --host 0.0.0.0 --port 8000 --reload
