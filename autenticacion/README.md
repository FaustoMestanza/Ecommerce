# Microservicio de Autenticacion

Este servicio centraliza registro, login y emision de JWT para la plataforma.

## Endpoints principales

- `POST /api/auth/register/`: registro publico con rate limit por scope `register`.
- `POST /api/auth/login/`: retorna `access` y `refresh`.
- `POST /api/auth/refresh/`: renueva `access` usando `refresh`.
- `GET /api/auth/me/`: endpoint privado para obtener el usuario autenticado.

## Ejecucion local

1. Entrar a `autenticacion/`.
2. Crear y activar entorno virtual: `python -m venv .venv` y `./.venv/Scripts/Activate.ps1`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Migrar base de datos: `python manage.py migrate`.
5. Levantar servidor: `python manage.py runserver`.

API base: `http://localhost:8000/api/auth/`.

## Variables de entorno para integrar con `usuarios`

- `USUARIOS_SERVICE_URL`: URL base del micro de usuarios.
  - local: `http://localhost:8000`
  - docker interno: `http://usuarios:8000`
- `USUARIOS_SERVICE_TOKEN`: token compartido para endpoints internos entre micros.

`autenticacion` delega en `usuarios`:
- registro: `POST {USUARIOS_SERVICE_URL}/api/users/`
- validacion de credenciales: `POST {USUARIOS_SERVICE_URL}/api/internal/auth-user/`
- perfil por id: `GET {USUARIOS_SERVICE_URL}/api/internal/users/{id}/`
