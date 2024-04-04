from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    """Кастомный класс разрешений для представлений."""

    def has_permission(self, request, view):
        return (
            (request.method in permissions.SAFE_METHODS)
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, views, obj):
        return (
            (request.method in permissions.SAFE_METHODS)
            or request.user.is_superuser
            or obj.author == request.user
        )
