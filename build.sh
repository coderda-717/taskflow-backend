#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=========================================="
echo "Starting Build Process"
echo "=========================================="

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input --clear

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --no-input

echo "=========================================="
echo "Build Complete!"
echo "=========================================="