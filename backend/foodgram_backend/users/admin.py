from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    """Custom fields for display in the admin's page."""

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password',
        'is_admin'
    )


admin.site.register(CustomUser, CustomUserAdmin)