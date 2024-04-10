from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from users.models import CustomUser, Subscription
from recipes.models import (
    Favorites,
    Recipe,
    ShoppingCart,
    Tag,
    Ingredient,
    IngredientsInRecipe
)


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
        context = self.context.get('request')
        return (
            context
            and context.user.is_authenticated
            and context.user.subscriptions.filter(
                subscribed_to=obj
            ).exists()
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписок."""

    class Meta:
        model = Subscription
        fields = ('subscriber', 'subscribed_to')

    def validate(self, data):
        """Метод валидации полей сериализатора."""
        subscriber = data.get('subscriber')
        subscribed_to = data.get('subscribed_to')
        if subscriber == subscribed_to:
            raise serializers.ValidationError(
                'Невозможно оформить подписку на свой профиль.'
            )
        if subscriber.subscriptions.filter(subscribed_to=subscribed_to):
            raise serializers.ValidationError(
                'Данный пользователь уже добавлен в подписки'
            )
        return data

    def to_representation(self, instance):
        """Метод представления сериализованных данных."""
        return SubscriptionGetSerializer(
            instance.subscribed_to, context=self.context
        ).data


class SubscriptionGetSerializer(UserSerializer):
    """Сериализатор для получения списка подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True,
        default=0,
        source='recipes.count'
    )

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        """Метод для получения списка рецептов."""
        query_params = self.context.get(
            'request'
        ).query_params.get('recipes_limit')
        recipe_data = obj.recipes.all()
        try:
            if query_params:
                recipe_data = recipe_data[:int(query_params)]
        except Exception:
            raise serializers.ValidationError(
                'Укажите "recipes_limit" целым положительным чиислом.'
            )
        return RecipeRepresentationSerializer(
            recipe_data,
            many=True,
            context=self.context
        ).data


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
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

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
        """Метод для отображения поля избранного."""
        context = self.context.get('request')
        return (
            context
            and context.user.is_authenticated
            and Favorites.objects.filter(
                user=context.user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Метод для отображения поля корзины покупок."""
        context = self.context.get('request')
        return (
            context
            and context.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=context.user,
                recipe=obj
            ).exists()
        )

    def get_ingredients(self, obj):
        """Метод для отображения поля ингредиентов."""
        queryset = obj.ingredients_in_recipe.all()
        return IngredientInRecipeSerializer(queryset, many=True).data


class IngredientInRecipeEditSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов для редактирования рецептов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientsInRecipe
        fields = (
            'id',
            'amount',
        )


class RecipeEditSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования рецептов."""

    ingredients = IngredientInRecipeEditSerializer(
        many=True,
        allow_null=False,
        allow_empty=False,
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    @staticmethod
    def add_ingredients(recipe, ingredients):
        """Метод для сохранения ингредиентов в рецепте."""
        return recipe.ingredients_in_recipe.bulk_create(
            [
                IngredientsInRecipe(
                    recipe=recipe,
                    ingredient=ingredient.get('id'),
                    amount=ingredient.get('amount')
                ) for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        """Метод создания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe=recipe, ingredients=ingredients)
        recipe.tags.set(tags, clear=True)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления рецептов."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags, clear=True)
        self.add_ingredients(recipe=instance, ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Метод изменения выходных данных сериализатора."""
        return RecipeSerializer(
            instance=instance,
            context=self.context
        ).data

    def validate(self, data):
        """Метод валидации полей тегов и ингредиентов."""
        if not data.get('ingredients'):
            raise serializers.ValidationError(
                'В рецепт не добавлены ингредиенты')
        ingredients_id = [
            ingredient.get('id').id
            for ingredient in data.get('ingredients')
        ]
        if not data.get('tags'):
            raise serializers.ValidationError(
                'В рецепт не добавлены теги')
        tags_id = [tag.id for tag in data.get('tags')]
        if len(ingredients_id) != len(set(ingredients_id)):
            raise serializers.ValidationError(
                'В рецепт добавлены повторяющиеся ингредиенты')
        if len(tags_id) != len(set(tags_id)):
            raise serializers.ValidationError(
                'В рецепт добавлены повторяющиеся теги')
        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Поле с изображением обязательно.')
        return value


class RecipeRepresentationSerializer(serializers.ModelSerializer):
    """Сериализатор для представлений корзины и избранного."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор корзины покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        """Метод валидации полей сериализатора."""
        if ShoppingCart.objects.filter(
            user=data.get('user'),
            recipe=data.get('recipe')
        ).exists():
            raise serializers.ValidationError(
                'Данный рецепт уже добавлен в корзину')
        return data

    def to_representation(self, instance):
        """Метод представления сериализованных данных."""
        return RecipeRepresentationSerializer(
            instance.recipe).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в избранное."""

    class Meta:
        model = Favorites
        fields = ('user', 'recipe')

    def validate(self, data):
        """Метод валидации полей сериализатора."""
        if Favorites.objects.filter(
            user=data.get('user'),
            recipe=data.get('recipe')
        ).exists():
            raise serializers.ValidationError(
                'Данный рецепт уже добавлен в избранное')
        return data

    def to_representation(self, instance):
        """Метод представления сериализованных данных."""
        return RecipeRepresentationSerializer(
            instance.recipe).data
