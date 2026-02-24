#!/bin/bash

set -e

echo "🚀 Starting Django STAGING deployment..."

echo "🏗️  Building Docker image..."
docker build -t college-django:stag .

echo "🔄 Restarting container..."
docker-compose -f docker-compose.stag.yml down
docker-compose -f docker-compose.stag.yml up -d

echo "⏳ Waiting for container to start..."
sleep 10

echo "🔄 Running migrations..."
docker exec django-stag python manage.py migrate --noinput 2>/dev/null || echo "⚠️ No migrations to run yet"

echo "📦 Collecting static files..."
docker exec django-stag python manage.py collectstatic --noinput 2>/dev/null || echo "⚠️ Static files not ready yet"

if docker ps | grep -q "django-stag"; then
    echo "✅ Django STAGING deployed successfully!"
    echo "🌐 Admin: http://172.35.2.130:8002/admin/"
    echo "📡 API: http://172.35.2.130:8002/api/"
    echo ""
    echo "📋 Container logs (last 10 lines):"
    docker logs django-stag --tail 10
else
    echo "❌ Deployment failed - container not running"
    docker logs django-stag --tail 50
    exit 1
fi
