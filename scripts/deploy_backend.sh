#!/bin/bash

# Backend Deployment Script for Railway/Render

set -e

echo "🚀 Starting backend deployment..."

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

echo "📦 Installing dependencies..."
pip install -r requirements/production.txt

echo "🗃️  Running migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Backend deployment preparation complete!"
echo "Use 'railway up' or your platform's CLI to deploy"
