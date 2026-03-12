#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Ensuring Django superuser exists..."
  python manage.py shell -c "from django.contrib.auth import get_user_model; import os; U=get_user_model(); username=os.getenv('DJANGO_SUPERUSER_USERNAME'); email=os.getenv('DJANGO_SUPERUSER_EMAIL'); password=os.getenv('DJANGO_SUPERUSER_PASSWORD'); U.objects.filter(username=username).exists() or U.objects.create_superuser(username=username, email=email, password=password)"
else
  echo "Superuser environment variables not set; skipping superuser creation."
fi

echo "Starting Gunicorn..."
exec gunicorn usuarios_service.wsgi:application --bind 0.0.0.0:8000
