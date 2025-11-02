# Official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY food.pkl .
COPY text_emb.pkl .
COPY tfidf_vectorizer.pkl .
COPY .env .

# Port 8000
EXPOSE 8000

# Commands to init app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]