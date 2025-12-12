FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install specific compatible versions
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir \
    redis==4.6.0 \
    numpy==1.24.3 \
    scikit-learn==1.3.0 \
    requests==2.31.0 \
    sentence-transformers==2.7.0 \
    huggingface_hub==0.19.4

# Copy your code
COPY *.py .
COPY *.json .

ENV PYTHONUNBUFFERED=1
ENV REDIS_HOST=redis

CMD ["python", "worker.py"]