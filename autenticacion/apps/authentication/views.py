from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import LoginRequestSerializer, RegisterRequestSerializer
from .users_client import (
    UsersServiceError,
    authenticate_user,
    get_user_by_id,
    register_user,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def post(self, request):
        serializer = RegisterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            status_code, data = register_user(serializer.validated_data)
        except UsersServiceError:
            return Response(
                {"detail": "No se pudo contactar al microservicio de usuarios."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(data, status=status_code)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            status_code, data = authenticate_user(
                serializer.validated_data["username"],
                serializer.validated_data["password"],
            )
        except UsersServiceError:
            return Response(
                {"detail": "No se pudo contactar al microservicio de usuarios."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if status_code != status.HTTP_200_OK:
            return Response(data, status=status_code)

        refresh = RefreshToken()
        refresh["user_id"] = data["id"]
        refresh["username"] = data["username"]
        refresh["email"] = data.get("email", "")

        access = refresh.access_token
        access["username"] = data["username"]
        access["email"] = data.get("email", "")

        return Response(
            {
                "access": str(access),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class PublicTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.auth.get("user_id")
        if not user_id:
            return Response(
                {"detail": "Token sin user_id."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            status_code, data = get_user_by_id(user_id)
        except UsersServiceError:
            return Response(
                {"detail": "No se pudo contactar al microservicio de usuarios."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(data, status=status_code)
