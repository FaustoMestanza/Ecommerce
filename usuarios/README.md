# Microservicio de Usuarios

Este servicio gestiona a los usuarios de la plataforma.

**Estructura principal**

- `usuarios_service/` – proyecto Django con configuración global.
- `apps/users/` – aplicación que define el modelo de usuario, serializador, vistas y rutas.
- `tests/` – pruebas de API que cubren operaciones básicas de usuarios.
- `Dockerfile`, `requirements.txt` – para construir la imagen.
- `CONTEXT.md` – archivo explicativo con más detalles.

**Cómo ejecutar localmente**

1. Crear entorno virtual y activar:
   ```bash
   python -m venv venv
   source venv/bin/activate  # o venv\Scripts\activate en Windows
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Migrar la base de datos:
   ```bash
   python manage.py migrate
   ```
4. Ejecutar servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```
5. La API estará disponible en `http://localhost:8000/api/users/`.

**Construir y ejecutar con Docker**

```bash
docker build -t usuarios-service .
docker run -p 8000:8000 usuarios-service
```

Ver también `CONTEXT.md` para una descripción general y guía ampliada.
