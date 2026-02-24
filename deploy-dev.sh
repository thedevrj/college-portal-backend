#!/bin/bash

set -e

echo "🚀 Starting Django DEV deployment..."

# Build Docker image
echo "🏗️  Building Docker image..."
docker build -t college-django:dev .

# Stop and remove old container
echo "🔄 Restarting container..."
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d

# Wait for container to be ready
echo "⏳ Waiting for container to start..."
sleep 10

# Run migrations
echo "🔄 Running migrations..."
docker exec django-dev python manage.py migrate --noinput 2>/dev/null || echo "⚠️ No migrations to run yet"

# Collect static files
echo "📦 Collecting static files..."
docker exec django-dev python manage.py collectstatic --noinput 2>/dev/null || echo "⚠️ Static files not ready yet"

# Check if container is running
if docker ps | grep -q "django-dev"; then
    echo "✅ Django DEV deployed successfully!"
    echo "🌐 Admin: http://172.35.2.130:8001/admin/"
    echo "📡 API: http://172.35.2.130:8001/api/"
    echo ""
    echo "📋 Container logs (last 10 lines):"
    docker logs django-dev --tail 10
else
    echo "❌ Deployment failed - container not running"
    docker logs django-dev --tail 50
    exit 1
fi
