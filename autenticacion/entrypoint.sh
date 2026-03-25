#!/bin/sh
set -e

echo "Starting Gunicorn..."
PORT_TO_BIND="${PORT:-8000}"
exec gunicorn autenticacion_service.wsgi:application --bind "0.0.0.0:${PORT_TO_BIND}"
