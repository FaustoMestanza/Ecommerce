# Contexto general del proyecto Ecommerce IA

Este documento describe el proyecto completo, no solo el microservicio de usuarios. La idea es tener una referencia rapida para cualquier desarrollador o agente que entre al repositorio.

## Lectura obligatoria para agentes

Antes de cualquier cambio, leer en este orden:

1. `AGENTS.md`
2. `CONTEXT.md`
3. README del microservicio a modificar

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

A la fecha, en este repositorio estan implementados de forma completa los servicios `usuarios` y `autenticacion`.

Los servicios `productos`, `inventario` y `carrito` ya estan considerados en CI/CD (workflows de GitHub Actions), pero sus carpetas aun no existen en el arbol del proyecto.

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
|-- autenticacion/
|   |-- apps/authentication/
|   |-- autenticacion_service/
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

## Estandar de seguridad obligatorio (todos los microservicios)

Cada microservicio nuevo debe implementar estas medidas desde el primer commit, usando `usuarios` como referencia:

- autenticacion JWT activa en DRF (`JWTAuthentication`) y permisos por defecto `IsAuthenticated`;
- endpoints publicos (por ejemplo registro/login) deben declarar permisos explicitos y no dejar acceso abierto por accidente;
- rate limiting obligatorio en DRF con `DEFAULT_THROTTLE_CLASSES`: `AnonRateThrottle`, `UserRateThrottle`, `ScopedRateThrottle`;
- `DEFAULT_THROTTLE_RATES` minimo: `anon=60/min`, `user=120/min`, y scope sensible `register=5/min`;
- operaciones publicas sensibles deben usar `throttle_scope` dedicado (ejemplo: `register`);
- `SECRET_KEY` nunca hardcodeado en produccion (solo variable de entorno);
- `DEBUG=False` en produccion;
- `ALLOWED_HOSTS` sin wildcard en produccion (no usar `"*"`);
- cookies seguras habilitadas en produccion: `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`;
- mantener `SECURE_CONTENT_TYPE_NOSNIFF=True` y `X_FRAME_OPTIONS="DENY"`;
- para despliegue detras de proxy HTTPS: `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`.

Variables de entorno recomendadas para seguridad (runtime):

- `JWT_SIGNING_KEY` (obligatoria en produccion; no reutilizar secretos debiles);
- `JWT_ALGORITHM` (default `HS256`, cambiar solo si hay estrategia definida);
- `JWT_ACCESS_MINUTES` (token corto, default recomendado: 30);
- `THROTTLE_ANON_RATE` (default `60/min`);
- `THROTTLE_USER_RATE` (default `120/min`);
- `THROTTLE_REGISTER_RATE` (default `5/min`);
- `DJANGO_SECRET_KEY` (obligatoria en produccion);
- `DJANGO_DEBUG` (`False` en produccion);
- `DJANGO_ALLOWED_HOSTS` (lista explicita de dominios).

Checklist minimo de pruebas de seguridad por microservicio:

- test de permisos para endpoints privados (anonimo debe recibir `401/403`);
- test de acceso por rol/propietario cuando aplique;
- test de rate limiting validando respuesta `429` al exceder cuota en endpoint sensible;
- test de registro/login para asegurar que el endpoint publico funciona dentro del limite configurado.

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
- `push` a `main`: ejecuta tests y, si pasan, publica imagen Docker y dispara despliegue en Render;
- la imagen se construye una sola vez en la etapa de publicacion (`push: true`), sin build duplicado.

Jobs esperados por pipeline:

- `TESTS`: instalar dependencias, migrar y ejecutar `python manage.py test`;
- `DOCKER HUB`: login con `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN`;
- `DOCKER IMAGE`: build y push de imagen del microservicio.
- `RENDER DEPLOY`: trigger de deploy via hook (`RENDER_DEPLOY_HOOK_USUARIOS`).

Secrets minimos en GitHub Actions:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `DJANGO_SECRET_KEY`
- `JWT_SIGNING_KEY` (recomendado cuando el emisor de JWT sea otro servicio)
- `RENDER_DEPLOY_HOOK_USUARIOS` (URL de Deploy Hook del servicio en Render)

Variables de entorno recomendadas para runtime (PaaS):

- `DATABASE_URL` (PostgreSQL, por ejemplo Neon)
- `REDIS_URL` (cuando actives cache distribuida con Redis)
- `DB_SSL_REQUIRE` (recomendado `True` para proveedores administrados como Neon)
- `USE_SQLITE_FOR_TESTS` (por defecto `True`, para que `manage.py test` no dependa de BD externa)

Nota operativa:

- `entrypoint.sh` no necesita cambios para Neon; al iniciar ejecuta migraciones usando la DB definida en `DATABASE_URL`.
- En Render, Gunicorn debe respetar el puerto dinamico via variable `PORT`.

## Flujo Git/GitHub recomendado

Para mantener orden y despliegue controlado:

1. Crear branch por trabajo (ejemplo: `feature/productos`).
2. Hacer commits y push en esa branch.
3. Abrir Pull Request hacia `main`.
4. Validar que tests de CI pasen.
5. Hacer merge a `main` para activar publicacion de imagen.

## Microservicios actualmente implementados: usuarios y autenticacion

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

Responsabilidades actuales de `autenticacion`:

- Registro de usuarios (`POST /api/auth/register/`) delegado al micro `usuarios`.
- Login JWT (`POST /api/auth/login/`) con validacion de credenciales contra `usuarios` y entrega de `access` y `refresh`.
- Renovacion de token (`POST /api/auth/refresh/`) sin reenviar credenciales.
- Endpoint privado de identidad (`GET /api/auth/me/`) protegido por JWT, con resolucion de perfil via `usuarios`.
- Configuracion de seguridad DRF/JWT y hardening base equivalente al estandar de `usuarios`.
- Pruebas de seguridad en `autenticacion/apps/authentication/tests/test_auth_api.py`.

Variables de integracion entre `autenticacion` y `usuarios`:

- `USUARIOS_SERVICE_URL`: URL base de `usuarios` (ej. `http://usuarios:8000`).
- `USUARIOS_SERVICE_TOKEN`: secreto compartido para endpoints internos (`X-Internal-Service-Token`).

## Ejecucion local (servicio usuarios)

1. Entrar a `usuarios/`.
2. Crear y activar entorno virtual: `python -m venv .venv` y `./.venv/Scripts/Activate.ps1`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Ejecutar migraciones: `python manage.py migrate`.
5. Levantar servidor: `python manage.py runserver`.
6. Probar en: `http://localhost:8000/api/users/`.

## Resumen

Este repositorio define una arquitectura de microservicios para ecommerce con estandares base de Django y CI/CD. Actualmente `usuarios` y `autenticacion` estan implementados y sirven como plantilla tecnica para construir el resto de microservicios con la misma estructura.
