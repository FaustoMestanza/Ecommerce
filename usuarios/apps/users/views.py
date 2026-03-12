"""Definiciones de vistas para endpoints relacionados con usuarios.

Utilizamos un `ModelViewSet` de DRF para ofrecer operaciones CRUD estándar
sobre el modelo User. El router (en urls.py) asignará los verbos HTTP a los
métodos correspondientes de forma automática.
"""

from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .serializers import UserSerializer


User = get_user_model()  # garantiza que respetamos la configuración AUTH_USER_MODEL


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet que provee `list`, `retrieve`, `create`, `update`, `destroy`.

    Los permisos no se establecen aquí todavía; por defecto será AllowAny. Se
    pueden aplicar restricciones o clases de permisos personalizadas más
    adelante (por ejemplo, sólo admins pueden listar todos los usuarios).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
