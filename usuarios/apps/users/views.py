"""Definiciones de vistas para endpoints relacionados con usuarios.

Utilizamos un `ModelViewSet` de DRF para ofrecer operaciones CRUD estándar
sobre el modelo User. El router (en urls.py) asignará los verbos HTTP a los
métodos correspondientes de forma automática.
"""

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth import get_user_model
from .permissions import IsSelfOrAdmin
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

    def get_throttles(self):
        # Aplica una cuota dedicada para registro publico.
        self.throttle_scope = "register" if self.action == "create" else None
        return super().get_throttles()

    def get_permissions(self):
        # Registro publico controlado (create). El resto requiere autenticacion.
        if self.action == "create":
            return [AllowAny()]

        # Operaciones globales reservadas a administradores.
        if self.action in {"list", "destroy"}:
            return [IsAdminUser()]

        # Acceso a recurso individual solo para duenio o admin.
        if self.action in {"retrieve", "update", "partial_update"}:
            return [IsAuthenticated(), IsSelfOrAdmin()]

        return [IsAuthenticated()]
