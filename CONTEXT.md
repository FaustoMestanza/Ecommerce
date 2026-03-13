# Contexto general del proyecto Ecommerce IA

Este documento describe el proyecto completo, no solo el microservicio de usuarios. La idea es tener una referencia rapida para cualquier desarrollador o agente que entre al repositorio.

## Vision del proyecto

Ecommerce IA es una arquitectura orientada a microservicios para una plataforma de comercio electronico. Cada dominio del negocio vive en un servicio independiente, con su propio ciclo de build, test y despliegue.

La comunicacion entre microservicios se realiza mediante APIs HTTP y payloads en formato JSON.

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
|   |-- entrypoint.sh
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

Adicionalmente, cada microservicio Django debe mantener esta base:

- estructura: `<micro>/apps/<app_principal>/`, `<micro>/<proyecto_django>/`, `manage.py`, `requirements.txt`, `Dockerfile`, `entrypoint.sh`;
- tests dentro de la app (ejemplo: `apps/users/tests/`);
- variables en `settings.py` con nombres consistentes: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`;
- base JWT en `settings.py` para validacion (`JWT_SIGNING_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_MINUTES`);
- base de cache preparada: Redis por `REDIS_URL` con fallback a `LocMemCache` para desarrollo/CI;
- comentarios breves en componentes clave (modelos, vistas, serializers, entrypoint) para explicar responsabilidad tecnica.

## Estandar de entorno local (VS Code + venv)

Para evitar errores de imports (por ejemplo `rest_framework` no encontrado), cada microservicio debe manejar su entorno virtual propio dentro de su carpeta:

- ruta esperada: `<microservicio>/.venv/`
- ejemplo: `usuarios/.venv/`

Regla para VS Code cuando se trabaja desde la raiz del monorepo:

- seleccionar siempre el interprete del microservicio activo, no el `.venv` de la raiz;
- para `usuarios`, usar: `C:\Users\faust\Documents\Ecommerce IA\usuarios\.venv\Scripts\python.exe`;
- si persisten avisos, ejecutar `Developer: Reload Window` y `Python: Restart Language Server`.

## Como funciona CI/CD en este repo

Cada microservicio tiene su propio pipeline (`ci-*.yml`) y sigue este patron:

- `pull_request` a `main`: ejecuta solo tests;
- `push` a `main`: ejecuta tests y, si pasan, publica imagen Docker;
- la imagen se construye una sola vez en la etapa de publicacion (`push: true`), sin build duplicado.

Jobs esperados por pipeline:

- `TESTS`: instalar dependencias, migrar y ejecutar `python manage.py test`;
- `DOCKER HUB`: login con `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN`;
- `DOCKER IMAGE`: build y push de imagen del microservicio.

Secrets minimos en GitHub Actions:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `DJANGO_SECRET_KEY`
- `JWT_SIGNING_KEY` (recomendado cuando el emisor de JWT sea otro servicio)

Variables de entorno recomendadas para runtime (PaaS):

- `DATABASE_URL` (PostgreSQL, por ejemplo Neon)
- `REDIS_URL` (cuando actives cache distribuida con Redis)
- `DB_SSL_REQUIRE` (recomendado `True` para proveedores administrados como Neon)
- `USE_SQLITE_FOR_TESTS` (por defecto `True`, para que `manage.py test` no dependa de BD externa)

Nota operativa:

- `entrypoint.sh` no necesita cambios para Neon; al iniciar ejecuta migraciones usando la DB definida en `DATABASE_URL`.

## Flujo Git/GitHub recomendado

Para mantener orden y despliegue controlado:

1. Crear branch por trabajo (ejemplo: `feature/productos`).
2. Hacer commits y push en esa branch.
3. Abrir Pull Request hacia `main`.
4. Validar que tests de CI pasen.
5. Hacer merge a `main` para activar publicacion de imagen.

## Microservicio actualmente implementado: usuarios

Responsabilidades actuales de `usuarios`:

- CRUD de cuentas de usuario via API REST.
- Exposicion de rutas de usuarios y endpoint de salud.
- Validacion de JWT para proteger endpoints.
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
2. Crear y activar entorno virtual: `python -m venv .venv` y `./.venv/Scripts/Activate.ps1`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Ejecutar migraciones: `python manage.py migrate`.
5. Levantar servidor: `python manage.py runserver`.
6. Probar en: `http://localhost:8000/api/users/`.

## Resumen

Este repositorio define una arquitectura de microservicios para ecommerce con estandares base de Django y CI/CD. `usuarios` es el servicio implementado y funciona como plantilla tecnica para construir el resto de microservicios con la misma estructura.
