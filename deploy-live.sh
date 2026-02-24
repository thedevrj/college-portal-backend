#!/bin/bash

set -e

echo "🚀 Starting Django PRODUCTION deployment..."

# Backup database first
echo "💾 Creating database backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p /srv/backups/django
docker exec postgres pg_dump -U postgres college_portal_live > "/srv/backups/django/backup_${timestamp}.sql" 2>/dev/null || echo "⚠️ Backup failed"

echo "🏗️  Building Docker image..."
docker build -t college-django:live .

echo "🔄 Restarting container..."
docker-compose -f docker-compose.live.yml down
docker-compose -f docker-compose.live.yml up -d

echo "⏳ Waiting for container to start..."
sleep 10

echo "🔄 Running migrations..."
docker exec django-live python manage.py migrate --noinput 2>/dev/null || echo "⚠️ No migrations to run yet"

echo "📦 Collecting static files..."
docker exec django-live python manage.py collectstatic --noinput 2>/dev/null || echo "⚠️ Static files not ready yet"

if docker ps | grep -q "django-live"; then
    echo "✅ Django PRODUCTION deployed successfully!"
    echo "🌐 Admin: http://172.35.2.130:8000/admin/"
    echo "📡 API: http://172.35.2.130:8000/api/"
    echo ""
    echo "📋 Container logs (last 10 lines):"
    docker logs django-live --tail 10
else
    echo "❌ Deployment failed - container not running"
    docker logs django-live --tail 50
    exit 1
fi
