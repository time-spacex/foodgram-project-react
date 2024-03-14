from django.core.mail import send_mail
from rest_framework import serializers, status

from users.models import CustomUser


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователей."""
    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
    
    def create(self, validated_data):
        """Метод для создания пользователей."""
        send_mail(
            subject='Создание пользователя Foodgram',
            message=('Добрый день! Вы создали пользователя: '
                     f'{validated_data.get("username")}'),
            from_email='mail@foodgram.com',
            recipient_list=[validated_data.get('email')],
            fail_silently=True
        )
        user = CustomUser.objects.create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user

    def to_representation(self, instance):
        """Метод для вывода сериализованных данных о пользователе."""
        data = super().to_representation(instance)
        data.pop('password', None)
        return data

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
        )