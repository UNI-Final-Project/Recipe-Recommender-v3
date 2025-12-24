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

# Port 8080
EXPOSE 8080

# Commands to init app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]