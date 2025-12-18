# ============================================
# Stage 1: Build Frontend (React + Vite)
# ============================================
FROM --platform=linux/amd64 node:20-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install ALL dependencies (including devDependencies needed for build)
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build static files for production
RUN npm run build

# ============================================
# Stage 2: Setup Backend (Python + FastAPI)
# ============================================
FROM --platform=linux/amd64 python:3.11-slim AS backend-builder

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# ============================================
# Stage 3: Final Runtime Image
# ============================================
FROM --platform=linux/amd64 python:3.11-slim

# Install Nginx and required system packages
RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy backend from Stage 2
WORKDIR /app
COPY --from=backend-builder /app/backend ./backend

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port 3000 (Nginx will listen here)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Start both Nginx and FastAPI
CMD ["/bin/bash", "/start.sh"]
