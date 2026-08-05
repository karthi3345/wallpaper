# Infrastructure

## Database
- **Type:** PostgreSQL 17 (manually installed, NOT the auto-provisioned MySQL)
- **Host:** 127.0.0.1
- **Port:** 5432
- **Database:** redwine_db
- **User:** redwine

## Background Service
- **Name:** django-server
- **Command:** `gunicorn store.wsgi:application --bind 0.0.0.0:8000 --workers 3`
- **Port:** 8000

## Caddy Proxy
- **Type:** reverse_proxy
- **Path:** / (root)
- **Target:** localhost:8000

## Environment Variables
- DJANGO_SECRET_KEY (secret)
- DJANGO_DEBUG (True/False)
- DJANGO_ALLOWED_HOSTS
- DB_NAME
- DB_USER
- DB_PASSWORD (secret)
- DB_HOST
- DB_PORT
- **POSTGRES_* vars (for PostgreSQL connection)**

## Static Files
- Tailwind via CDN (no build step)
- Custom CSS/JS in /static/
- Product images from external demo URLs

## Setup Script
1. Install Python dependencies (pip install -r requirements.txt)
2. Run migrations (python3 manage.py migrate)
3. Seed demo data (python3 manage.py seed_demo)
4. Collect static files (python3 manage.py collectstatic --noinput)
