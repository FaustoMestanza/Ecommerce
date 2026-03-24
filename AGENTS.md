# AGENTS - Guia operativa para agentes y subagentes

Este archivo define como trabajar en este repositorio de forma consistente.

## Orden de lectura al iniciar sesion

1. `AGENTS.md` (este archivo)
2. `CONTEXT.md`
3. README del microservicio a intervenir (ejemplo: `usuarios/README.md`)

## Reglas obligatorias de trabajo

- No romper funcionalidades existentes.
- No exponer secretos en codigo, logs o commits.
- Mantener cambios pequenos, claros y verificables.
- Si una decision tecnica cambia arquitectura o seguridad, actualizar `CONTEXT.md`.

## Flujo estandar por tarea

1. Revisar contexto y archivos afectados.
2. Implementar cambios minimos necesarios.
3. Ejecutar pruebas del microservicio afectado.
4. Reportar:
- que se cambio;
- por que;
- que pruebas se ejecutaron;
- riesgos pendientes.

## Estandar de seguridad minimo (todos los micros)

- DRF con JWT activo para endpoints privados.
- Permisos por defecto `IsAuthenticated`.
- Endpoints publicos con permiso explicito.
- Rate limiting obligatorio:
- `AnonRateThrottle`
- `UserRateThrottle`
- `ScopedRateThrottle`
- tasas base recomendadas:
- `anon=60/min`
- `user=120/min`
- `register=5/min`
- Hardening de produccion:
- `DEBUG=False`
- `ALLOWED_HOSTS` explicito (sin `*`)
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_CONTENT_TYPE_NOSNIFF=True`
- `X_FRAME_OPTIONS="DENY"`

## Reglas de pruebas minimas

- Probar permisos (anonimo vs autenticado).
- Probar reglas de rol/propietario cuando aplique.
- Probar rate limiting (`429`) en endpoint sensible.
- Ejecutar `python manage.py test` del microservicio tocado.

## Convencion para nuevos microservicios

- Estructura: `<micro>/apps/<app_principal>/`, `<micro>/<proyecto_django>/`, `manage.py`, `requirements.txt`, `Dockerfile`, `entrypoint.sh`.
- Entorno virtual propio: `<micro>/.venv/`.
- CI propio (`.github/workflows/ci-<micro>.yml`).

## Cuando usar subagentes

Usar subagentes solo cuando el trabajo se pueda paralelizar sin pisar archivos:

- subagente 1: seguridad;
- subagente 2: pruebas;
- subagente 3: documentacion.

Cada subagente debe reportar archivos tocados y resultado de validacion.
