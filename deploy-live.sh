#!/bin/bash

set -e

echo "🚀 Starting Django PRODUCTION deployment..."

# Backup database
echo "💾 Creating database backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p /srv/backups/django

docker exec postgres pg_dump -U postgres college_portal_live \
  > "/srv/backups/django/backup_${timestamp}.sql" \
  || echo "⚠️ Backup failed"

echo "🏗️ Building and deploying container..."
docker-compose -f docker-compose.live.yml down
docker-compose -f docker-compose.live.yml up -d --build

echo "🔍 Checking container status..."

if docker ps | grep -q "django-live"; then
    echo "✅ Django PRODUCTION deployed successfully!"
     echo "🌐 Admin: http://192.168.0.8:8000/admin/"
    echo "📡 API: http://192.168.0.8:8000/api/"
   echo ""
    echo "📋 Container logs (last 10 lines):"
    docker logs django-live --tail 10
else
    echo "❌ Deployment failed - container not running"
    docker logs django-live --tail 50
    exit 1
fi
