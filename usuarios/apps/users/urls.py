"""Enrutamiento de URLs para la app `users`.

Usamos el `DefaultRouter` de DRF para generar automáticamente el conjunto
estandar de rutas para el `UserViewSet` (p. ej. `/users/`, `/users/{pk}/`).
Se pueden agregar endpoints personalizados abajo si se necesitan.
"""

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)  # registra todas las rutas CRUD

urlpatterns = [
    path("", include(router.urls)),
    # futuro: agregar rutas personalizadas aquí, ej. path('profile/', profile_view)
]
