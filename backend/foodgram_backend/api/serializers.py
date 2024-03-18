from django.core.mail import send_mail
from rest_framework import serializers, status

from users.models import CustomUser
from recipes.models import Recipe, Tag, Ingredient


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
    """Сериализатор для работы с созданными пользователями."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Метод для отображения поля подписок."""
        for subscriber in obj.subscribers.all():
            if self.context.user.id == subscriber.subscriber_id:
                return True
        return False


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатов для рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )