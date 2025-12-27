#!/usr/bin/env bash
set -o errexit

echo "=========================================="
echo "Starting Build Process"
echo "=========================================="

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "Running database migrations..."
python manage.py migrate --no-input

echo "Creating superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'AdminPassword123!')
    print('Superuser created!')
else:
    print('Superuser already exists')
END

echo "=========================================="
echo "Build Complete!"
echo "=========================================="