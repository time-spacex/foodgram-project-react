from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from foodgram_backend.settings import (
    MAX_USERS_CHARFIELD_LENGTH)


class CustomUser(AbstractUser):
    """Класс кастомной модели пользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX_USERS_CHARFIELD_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_USERS_CHARFIELD_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_USERS_CHARFIELD_LENGTH
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name'
    ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Класс модели подписок пользователей."""
    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscribed_to = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        unique_together = ('subscriber', 'subscribed_to',)
