FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir requests

# Copy generator script and config
COPY generate_logs.py .

# Default command
CMD ["python", "generate_logs.py", "--url", "http://shadowguard-collector:8000/logs", "--batch-size", "50", "--delay", "2"]
