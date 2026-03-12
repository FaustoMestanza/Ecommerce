"""Definiciones de modelos para la app 'users'.

Este módulo declara el modelo de usuario personalizado para el microservicio
`usuarios`. Heredamos de `AbstractUser` de Django para obtener todos los
campos integrados (username, email, nombre, apellido, contraseña, etc.) y
mantener la opción de añadir campos extra más adelante sin alterar el modelo
autenticación por defecto.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Actualmente no agregamos campos nuevos; la clase existe para poder
    # referenciar `settings.AUTH_USER_MODEL` y ampliarla cuando las necesidades
    # del negocio lo requieran (por ejemplo, añadir `phone_number`,
    # `is_premium`, etc.).
    pass
