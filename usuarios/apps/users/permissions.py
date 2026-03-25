"""Permisos personalizados para proteger operaciones sobre usuarios."""

import os

from rest_framework.permissions import BasePermission


class IsSelfOrAdmin(BasePermission):
    """Permite acceso si el usuario autenticado es el dueño del recurso o admin."""

    def has_object_permission(self, request, view, obj):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or obj.pk == request.user.pk)
        )


class HasInternalServiceToken(BasePermission):
    """Permite acceso solo a servicios internos con token compartido."""

    def has_permission(self, request, view):
        expected_token = os.environ.get("USUARIOS_SERVICE_TOKEN", "").strip()
        provided_token = request.headers.get("X-Internal-Service-Token", "").strip()
        return bool(expected_token) and expected_token == provided_token
