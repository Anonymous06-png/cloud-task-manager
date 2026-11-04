# Django Cloud Task Manager
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY manage.py .
COPY config/ ./config/
COPY tasks/ ./tasks/
COPY templates/ ./templates/
COPY static/ ./static/
COPY locale/ ./locale/

# Create non-root user
RUN useradd -m -u 1000 django && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Collect static files (will be done at runtime with volume mount)
# RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health/').read()"

# Expose port
EXPOSE 8080

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "--timeout", "60", "config.wsgi:application"]
