from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from foodgram_backend.settings import MAX_CHARFIELD_LENGTH, MAX_EMAILFIELD_LENGTH


class CustomUser(AbstractUser):
    """Класс кастомной модели пользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=MAX_EMAILFIELD_LENGTH
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=MAX_CHARFIELD_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
        ]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_CHARFIELD_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_CHARFIELD_LENGTH
    )
    is_admin = models.BooleanField(
        verbose_name='Администратор',
        default=False,
        help_text=('Поле указывает, является ли данный '
                   'пользователь администратором')
    )

    def save(self, *args, **kwargs):
        """Кастомный метод сохранения пользователей."""
        if self.is_admin or self.is_staff:
            self.is_admin = True
            self.is_staff = True
        super().save(*args, **kwargs)


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
