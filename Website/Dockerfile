# =============================================================================
# DeepLearnX Production Dockerfile
# Multi-Domain Cognitive Diagnostic & Knowledge Gap Detection Platform
# =============================================================================

FROM python:3.10-slim

# Set environment flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8055

WORKDIR /app

# Install system dependencies (curl for health check)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU wheels and project dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# Copy application source code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY model/ ./model/
COPY database/ ./database/
COPY dataset/ ./dataset/
COPY run.py .

# Create volume mount points
VOLUME ["/app/database", "/app/model"]

# Expose internal application port
EXPOSE 8055

# Container healthcheck against /api/health
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8055/api/health || exit 1

# Launch production server via unified runner
CMD ["python", "run.py"]
