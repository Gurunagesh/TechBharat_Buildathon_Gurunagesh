FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for PyMySQL and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create uploads directory (runtime artefact, not committed)
RUN mkdir -p /app/uploads

# Expose FastAPI port
EXPOSE 8000

# Health check (matches /api/health endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
