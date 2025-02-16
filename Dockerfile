FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=False \
    DJANGO_SETTINGS_MODULE=cantine.settings \
    PYTHONPATH="${PYTHONPATH}:/app"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    # Add postgresql-client for potential database operations
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
RUN mkdir -p /app
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p \
    src/static \
    staticfiles \
    media \
    templates

# Collect static files and run migrations during build (cached)
RUN python manage.py collectstatic --noinput --clear

# Database setup and migration (will run on every container start)
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 cantine.wsgi:application"]

# Expose port and health check
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health/ || exit 1