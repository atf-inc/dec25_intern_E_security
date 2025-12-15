FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for redis
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install redis package (needed for behavior analysis)
RUN pip install --no-cache-dir redis

# Copy all worker files
COPY . .

# Run the behavior analysis monitor
CMD ["python", "-u", "test_behavior_redis.py"]
