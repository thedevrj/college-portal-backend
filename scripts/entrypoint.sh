#!/bin/bash

set -e

echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "PostgreSQL started"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
if [ "$DJANGO_ENV" = "live" ] || [ "$DJANGO_ENV" = "stag" ]; then
    exec gunicorn college_backend_portal.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-5}
else
    exec python manage.py runserver 0.0.0.0:8000
fi
