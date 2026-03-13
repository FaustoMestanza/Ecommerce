"""Permisos personalizados para proteger operaciones sobre usuarios."""

from rest_framework.permissions import BasePermission


class IsSelfOrAdmin(BasePermission):
    """Permite acceso si el usuario autenticado es el dueño del recurso o admin."""

    def has_object_permission(self, request, view, obj):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or obj.pk == request.user.pk)
        )
