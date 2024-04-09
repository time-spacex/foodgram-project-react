from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Subscription


class CustomUserAdmin(UserAdmin):
    """Custom fields for display in the admin's page."""

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password'
    )
    list_filter = ('email', 'username')


class SubscriptionAdmin(admin.ModelAdmin):
    """Административная конфигурация для модели подписок."""

    list_display = ('subscriber', 'subscribed_to')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
