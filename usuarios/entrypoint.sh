#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Ensuring Django superuser exists..."
  python manage.py shell <<'PYCODE'
import os
from django.contrib.auth import get_user_model

# 1) Obtener el modelo de usuario configurado en Django (AUTH_USER_MODEL)
User = get_user_model()

# 2) Leer credenciales desde variables de entorno del contenedor
username = os.getenv("DJANGO_SUPERUSER_USERNAME")
email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

# 3) Crear el superusuario solo si no existe (operacion idempotente)
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
PYCODE
else
  echo "Superuser environment variables not set; skipping superuser creation."
fi

echo "Starting Gunicorn..."
exec gunicorn usuarios_service.wsgi:application --bind 0.0.0.0:8000
