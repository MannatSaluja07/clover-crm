# Clover CRM — production container image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering output — makes
# container logs show up immediately instead of being buffered.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies needed to build psycopg2 (PostgreSQL driver)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files at build time so WhiteNoise can serve them
RUN python manage.py collectstatic --noinput --settings=crm_project.settings || true

EXPOSE 8000

# Run database migrations, then start the app with Gunicorn (production
# WSGI server — Django's own runserver is not meant for production use).
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn crm_project.wsgi:application --bind 0.0.0.0:8000 --workers 3"]
