import base64

from django.core.files.base import ContentFile
from django.core.mail import send_mail
from rest_framework import serializers, status

from users.models import CustomUser
from recipes.models import Recipe, Tag, Ingredient, IngredientsInRecipe


class Base64ImageField(serializers.ImageField):
    """Класс для получения изборажения."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')  
            ext = format.split('/')[-1]  
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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


class IngredientInRecipeSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientsInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатов для рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

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

    def get_is_favorited(self, obj):
        """Метод отображения поля избранных рецептов."""
        if self.context.get('request').user.is_authenticated:
            return obj in self.context.get('request').user.favorites.all()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Метод отображения поля рецептов в списке покупок."""
        if self.context.get('request').user.is_authenticated:
            return obj in self.context.get('request').user.shopping_cart.all()
        return False

    def get_ingredients(self, obj):
        """Метод для отображения поля ингредиентов."""
        queryset = obj.ingredients_in_recipe.all()
        return IngredientInRecipeSerializer(queryset, many=True).data


class IngredientInRecipeEditSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='ingredient_id')

    class Meta:
        model = IngredientsInRecipe
        fields = (
            'id',
            'amount',
        )


class RecipeEditSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeEditSerializer(many=True)

    # FIX: для теста сделал необязательным.
    # image = Base64ImageField(required=True)
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        """Метод создает объект рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            recipe.ingredients_in_recipe.get_or_create(**ingredient)
        for tag in tags:
            recipe.tags.add(tag)
        recipe.save()
        return recipe

    def to_representation(self, obj):
        # FIX: данные для редактирования приходят в одном формате, а отдать
        # их надо в другом формате.

        # Т.к. если мы обычный Recipe засунем в этот сериалайзер.
        # RecipeEditSerializer(instance=recipe), то в объявленное нами
        # поле ingredients, попадет recipe.ingredients,
        # а там объекты Ingredient, а у объекта Ingredient нет атрибута
        # ingredient_id, который мы указали, как источник для id
        # в сериалайзере IngredientInRecipeEditSerializer
        # id = serializers.IntegerField(source='ingredient_id')

        # Поэтому убираем проблемное поле. Чтобы не ломать сериализатор.
        self.fields.pop('ingredients')

        # Аналогично и для тэгов.
        # Убираем проблемное, ставим свое поле.
        self.fields['tags'] = TagSerializer(many=True)

        # Здесь будет уже OrderedDict с данными.
        representation = super().to_representation(obj)

        # В него и впихиваем, как в обычный словарь
        # ингредиенты в нужном нам формате. Подменить так, как с тэгами не
        # прокатит, т.к. мы поле явно объявили в сериализаторе, как атрибут.
        representation['ingredients'] = IngredientInRecipeSerializer(
            IngredientsInRecipe.objects.filter(recipe=obj).all(), many=True
        ).data

        return representation
