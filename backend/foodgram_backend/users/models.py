from django.db import models
from django.db.models import F, Q
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from foodgram_backend.constants import (
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
        related_name='subscriptions',
        verbose_name='подписчик'
    )
    subscribed_to = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='подписан на'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribed_to'],
                name='unique_subscriber_and_subscribed_to'
            ),
            models.CheckConstraint(
                check=~Q(subscriber=F('subscribed_to')),
                name='prevent_self_subscription'
            ),
        ]
