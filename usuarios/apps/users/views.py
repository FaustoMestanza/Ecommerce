"""Definiciones de vistas para endpoints relacionados con usuarios.

Utilizamos un `ModelViewSet` de DRF para ofrecer operaciones CRUD estándar
sobre el modelo User. El router (en urls.py) asignará los verbos HTTP a los
métodos correspondientes de forma automática.
"""

from rest_framework import viewsets
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .permissions import HasInternalServiceToken, IsSelfOrAdmin
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


class InternalAuthUserView(APIView):
    """Valida credenciales y retorna datos del usuario para otros micros."""

    authentication_classes = []
    permission_classes = [HasInternalServiceToken]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "username y password son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=username, password=password)
        if not user:
            return Response(
                {"detail": "Credenciales invalidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"detail": "Usuario inactivo."},
                status=status.HTTP_403_FORBIDDEN,
            )

        payload = {
            "id": user.pk,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
        }
        return Response(payload, status=status.HTTP_200_OK)


class InternalUserByIdView(APIView):
    """Retorna datos basicos por id para validacion de token en otros micros."""

    authentication_classes = []
    permission_classes = [HasInternalServiceToken]

    def get(self, request, user_id: int):
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response(
                {"detail": "Usuario no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = {
            "id": user.pk,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
        }
        return Response(payload, status=status.HTTP_200_OK)
