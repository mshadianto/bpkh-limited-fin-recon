# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║                    AURIX RECONCILIATION MODULE - DOCKER                       ║
# ║                           BPKH Limited - Production                           ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

FROM python:3.11-slim

# Cache-bust arg to force rebuild
ARG CACHEBUST=1

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker cache optimization)
COPY requirements-base.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-base.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 aurix && chown -R aurix:aurix /app
USER aurix

# Railway injects $PORT at runtime; default to 8501 for local Docker
ENV PORT=8501
EXPOSE 8501

# No HEALTHCHECK — let Railway handle it externally

# Start: use shell form so $PORT is expanded at runtime
CMD streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false
