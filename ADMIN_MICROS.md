# Admin Django por microservicio

Este estandar aplica a cada microservicio Django del proyecto.

## Objetivo

- Tener acceso a panel `/admin` para operacion y soporte.
- Crear superusuario de forma idempotente en despliegue.
- Evitar exponer el admin sin controles basicos.

## Requisitos minimos por micro

1. Incluir `admin.py` en la app principal y registrar los modelos clave.
2. Mantener `django.contrib.admin` en `INSTALLED_APPS`.
3. Exponer ruta `admin/` en `urls.py`.
4. En `entrypoint.sh`, ejecutar migraciones y creacion opcional de superusuario.

## Variables de entorno para superusuario

- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

Si existen las 3 variables, el micro debe crear el superusuario solo si no existe.

## Seguridad minima recomendada para admin en produccion

- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS` explicito
- `DJANGO_SESSION_COOKIE_SECURE=True`
- `DJANGO_CSRF_COOKIE_SECURE=True`
- `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`

## Checklist rapido de validacion

1. Abrir `/admin` y autenticar con superusuario.
2. Confirmar que se listan modelos registrados.
3. Verificar en logs que `python manage.py migrate --noinput` corre al iniciar.
4. Verificar que re-despliegue no crea duplicado de superusuario.

