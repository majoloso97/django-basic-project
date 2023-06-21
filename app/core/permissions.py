from rest_framework import permissions


class SuperUserOnlyPermission(permissions.BasePermission):
    message = 'User has to be an admin, a coach or a cohort admin to have access.'

    def has_permission(self, request, view):
        current_user = request.user
        return current_user.is_superuser
    