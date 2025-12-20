FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir requests

# Copy generator script and config
COPY generate_logs.py .

# Default command - Run shadow_ai scenario with 5s delay between logs
# Change -t to: blacklist, whitelist, or all to test different scenarios
# Adjust --delay to control speed (in seconds)
CMD ["python", "generate_logs.py", "--type", "all", "--url", "http://shadowgaurd-collector:8000/logs", "--delay", "5"]
