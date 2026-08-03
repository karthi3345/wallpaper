#!/bin/bash
set -e

echo "=== Red and Wine Decor — Setup ==="

# Install PostgreSQL if not present
if ! command -v psql &>/dev/null; then
    echo "Installing PostgreSQL..."
    sudo apt-get update -qq
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq postgresql-17 postgresql-client-17
fi

# Start PostgreSQL
echo "Starting PostgreSQL..."
sudo pg_ctlcluster 17 main start 2>/dev/null || true
sleep 2

# Create database and user (idempotent)
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='redwine'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER redwine WITH PASSWORD 'redwine2026' SUPERUSER;"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='redwine_db'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE redwine_db OWNER redwine;"

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --break-system-packages -q -r /workspace/requirements.txt

# Django setup
cd /workspace
export PATH="$HOME/.local/bin:$PATH"

echo "Running migrations..."
python3 manage.py migrate --noinput

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Seed demo data if database is empty
PRODUCT_COUNT=$(PGPASSWORD=redwine2026 psql -U redwine -d redwine_db -h 127.0.0.1 -t -c "SELECT COUNT(*) FROM shop_product;" 2>/dev/null || echo "0")
if [ "$PRODUCT_COUNT" -eq 0 ] 2>/dev/null; then
    echo "Seeding demo data..."
    python3 manage.py seed_demo
    python3 manage.py seed_geo
    python3 manage.py seed_geo_all
    python3 manage.py update_country_landmarks
else
    echo "Demo data already present ($PRODUCT_COUNT products). Skipping seed."
fi

# Create superuser if not exists
python3 -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@redwine.local', 'admin123')
    print('Superuser created: admin / admin123')
" 2>/dev/null || echo "Superuser check done."

echo "=== Setup Complete ==="
