# Contexto general del proyecto Ecommerce IA

Este documento describe el proyecto completo, no solo el microservicio de usuarios. La idea es tener una referencia rapida para cualquier desarrollador que entre al repositorio.

## Vision del proyecto

Ecommerce IA es una arquitectura orientada a microservicios para una plataforma de comercio electronico. Cada dominio del negocio vive en un servicio independiente, con su propio ciclo de build, test y despliegue.
La comunicacion entre microservicios se realiza mediante APIs HTTP y payloads en formato JSON.
Crear un .venv 
Al crear cada componente de django dame comentarios para saber que hace cada parte del código

Servicios contemplados en la arquitectura:

- `usuarios`
- `productos`
- `inventario`
- `autenticacion`
- `carrito`

## Estado actual del repositorio

A la fecha, en este repositorio solo esta implementado de forma completa el servicio `usuarios`.

Los servicios `productos`, `inventario`, `autenticacion` y `carrito` ya estan considerados en CI/CD (workflows de GitHub Actions), pero sus carpetas aun no existen en el arbol del proyecto.

## Estructura actual

```text
Ecommerce IA/
|-- .github/
|   `-- workflows/
|       |-- ci-usuarios.yml
|       |-- ci-productos.yml
|       |-- ci-inventario.yml
|       |-- ci-autenticacion.yml
|       `-- ci-carrito.yml
|-- usuarios/
|   |-- apps/users/
|   |-- usuarios_service/
|   |-- tests/
|   |-- Dockerfile
|   |-- requirements.txt
|   `-- manage.py
`-- CONTEXT.md
```

## Stack tecnico base

- Python 3.11
- Django 4.2
- Django REST Framework
- Gunicorn
- SQLite para desarrollo local (con posibilidad de migrar a PostgreSQL)
- Docker para empaquetado de servicios
- GitHub Actions para CI/CD

## Estandar obligatorio por microservicio

Cada microservicio debe incluir un archivo `entrypoint.sh` para produccion con estas responsabilidades minimas:

- ejecutar `python manage.py migrate --noinput` al iniciar el contenedor;
- crear superusuario de forma opcional e idempotente usando variables de entorno (`DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`);
- iniciar Gunicorn como proceso principal.

## Como funciona CI/CD en este repo

Cada microservicio tiene su propio pipeline (`ci-*.yml`), que corre por cambios en la carpeta del servicio y publica su imagen Docker correspondiente.

Nota: mientras no existan las carpetas de los servicios faltantes, esos workflows no estaran listos para una ejecucion completa.

## Microservicio actualmente implementado: usuarios

Responsabilidades actuales de `usuarios`:

- CRUD de cuentas de usuario via API REST.
- Exposicion de rutas de usuarios y endpoint de salud.
- Base para estandarizar futuros microservicios.

Rutas y componentes clave:

- `usuarios/usuarios_service/settings.py`: configuracion general.
- `usuarios/apps/users/models.py`: modelo `User` basado en `AbstractUser`.
- `usuarios/apps/users/serializers.py`: serializacion de usuarios.
- `usuarios/apps/users/views.py`: `ModelViewSet` para CRUD.
- `usuarios/apps/users/urls.py`: enrutado del modulo usuarios.
- `usuarios/apps/users/tests/test_users_api.py`: pruebas basicas del API.
- `usuarios/entrypoint.sh`: inicializacion de produccion (migraciones, superusuario opcional y arranque).

## Ejecucion local (servicio usuarios)

1. Entrar a `usuarios/`.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Ejecutar migraciones: `python manage.py migrate`.
4. Levantar servidor: `python manage.py runserver`.
5. Probar en: `http://localhost:8000/api/users/`.

## Hoja de ruta recomendada

Para alinear repo y arquitectura declarada:

1. Crear carpetas base para `productos`, `inventario`, `autenticacion` y `carrito`.
2. Replicar estructura minima usada en `usuarios` (Django project, app, tests, Dockerfile, requirements).
3. Definir contratos HTTP entre servicios (por ejemplo, validacion de usuario para carrito).
4. Agregar `docker-compose.yml` raiz para orquestar entorno local multi-servicio.
5. Homologar convenciones de settings, logging, health checks y pruebas.

## Resumen

Este repositorio ya define claramente una arquitectura de microservicios para ecommerce, con CI/CD preparado para 5 dominios. Hoy, `usuarios` es el unico servicio implementado y funciona como plantilla tecnica para completar el resto de servicios.
