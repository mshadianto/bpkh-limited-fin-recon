# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║                    AURIX RECONCILIATION MODULE - DOCKER                       ║
# ║                           BPKH Limited - Production                           ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker cache optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 aurix && chown -R aurix:aurix /app
USER aurix

# Expose port
EXPOSE 8501

# Health check (uses $PORT which Railway overrides)
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

# Run the application on $PORT (Railway injects its own PORT value)
CMD sh -c "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"
