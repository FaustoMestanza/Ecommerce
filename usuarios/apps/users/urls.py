"""Enrutamiento de URLs para la app `users`.

Usamos el `DefaultRouter` de DRF para generar automáticamente el conjunto
estandar de rutas para el `UserViewSet` (p. ej. `/users/`, `/users/{pk}/`).
Se pueden agregar endpoints personalizados abajo si se necesitan.
"""

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import InternalAuthUserView, InternalUserByIdView, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)  # registra todas las rutas CRUD

urlpatterns = [
    path("", include(router.urls)),
    path("internal/auth-user/", InternalAuthUserView.as_view(), name="internal-auth-user"),
    path("internal/users/<int:user_id>/", InternalUserByIdView.as_view(), name="internal-user-by-id"),
    # futuro: agregar rutas personalizadas aquí, ej. path('profile/', profile_view)
]
