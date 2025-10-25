# Official Python image
FROM python:3.9-slim

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
COPY embedder.pkl .
COPY .env .

# Cloud Run requires port 8080
EXPOSE 8080

# Commands to init app using gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "1"]