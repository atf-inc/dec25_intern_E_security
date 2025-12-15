FROM python:3.11-slim

WORKDIR /workspace

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire build context (collector directory) into /workspace/collector
# This preserves the package structure so imports like "from collector.app..." work
COPY . ./collector

# Add /workspace to PYTHONPATH so python can find the 'collector' package
ENV PYTHONPATH=/workspace

EXPOSE 8000

# Run the app using the package path
CMD ["uvicorn", "collector.main:app", "--host", "0.0.0.0", "--port", "8000"]
