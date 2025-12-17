#!/bin/bash

# Exit on any error
set -e

echo "Starting ShadowGuard Dashboard..."

# Start Nginx in the background
echo "Starting Nginx..."
nginx -g 'daemon off;' &
NGINX_PID=$!

# Wait a moment for Nginx to start
sleep 2

# Start FastAPI backend with Uvicorn
echo "Starting FastAPI backend..."
cd /app/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --log-level info &
BACKEND_PID=$!

# Function to handle shutdown gracefully
shutdown() {
    echo "Shutting down services..."
    kill -TERM $NGINX_PID 2>/dev/null || true
    kill -TERM $BACKEND_PID 2>/dev/null || true
    wait $NGINX_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
    echo "Shutdown complete"
    exit 0
}

# Trap termination signals
trap shutdown SIGTERM SIGINT

echo "Dashboard services started successfully!"
echo "Nginx PID: $NGINX_PID"
echo "Backend PID: $BACKEND_PID"
echo "Dashboard accessible at http://localhost:3000"

# Wait for both processes
wait $NGINX_PID $BACKEND_PID
