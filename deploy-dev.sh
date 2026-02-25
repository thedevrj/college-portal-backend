#!/bin/bash

set -e

echo "🚀 Starting Django DEV deployment..."

echo "📦 Building and starting container..."
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d --build

echo "🔍 Checking container status..."

if docker ps | grep -q "django-dev"; then
    echo "✅ Django DEV deployed successfully!"
    echo "🌐 Admin: http://172.35.0.45:8001/admin/"
    echo "📡 API: http://172.35.0.45:8001/api/"
   echo ""
    echo "📄 Container logs (last 10 lines):"
    docker logs django-dev --tail 10
else
    echo "❌ Deployment failed - container not running"
    docker logs django-dev --tail 50
    exit 1
fi
