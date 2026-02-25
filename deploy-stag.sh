#!/bin/bash

set -e

echo "🚀 Starting Django STAGING deployment..."

echo "📦 Building and starting container..."
docker-compose -f docker-compose.stag.yml down
docker-compose -f docker-compose.stag.yml up -d --build

echo "🔍 Checking container status..."

if docker ps | grep -q "django-stag"; then
    echo "✅ Django STAGING deployed successfully!"
    echo "🌐 Admin: http://172.35.0:45:8002/admin/"
    echo "📡 API: http://172.35.0.45:8002/api/"
   echo ""
    echo "📄 Container logs (last 10 lines):"
    docker logs django-stag --tail 10
else
    echo "❌ Deployment failed - container not running"
    docker logs django-stag --tail 50
    exit 1
fi
