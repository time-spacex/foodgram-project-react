from django.core.mail import send_mail
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from users.models import CustomUser, Subscription
from recipes.models import Recipe, Tag, Ingredient, IngredientsInRecipe


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
        if (
            context
            and context.user.is_authenticated
            and context.user.subscriptions.filter(
                subscribed_to=obj
            ).exists()
        ):
            return True
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для создания подписок."""

    class Meta:
        model =Subscription
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
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        """Метод для получения списка рецептов."""
        query_params = self.context.get(
            'request'
        ).query_params.get('recipes_limit')
        recipe_data = obj.recipes.all()
        if query_params:
            recipe_data = recipe_data[0:int(query_params)]
        return FavoriteSerializer(
            recipe_data,
            many=True,
            context=self.context
        ).data
    
    def get_is_subscribed(self, obj):
        """Метод для получения поля подписки."""
        return super().get_is_subscribed(obj)


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
    
    def add_ingredients(self, recipe, ingredients):
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
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe=recipe, ingredients=ingredients)
        recipe.tags.set(tags, clear=True)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        """Метод обновления рецептов."""
        self.validate_tags(validated_data.get('tags'))
        instance.tags.set(validated_data.get('tags'), clear=True)
        self.validate_ingredients(validated_data.get('ingredients'))
        instance.ingredients.clear()
        for ingredient in validated_data.get('ingredients'):
            instance.ingredients_in_recipe.create(**ingredient)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        return instance
  
    def get_is_favorited(self, obj):
        """Метод для отображения поля избранного."""
        context = self.context.get('request')
        if (
            context
            and context.user.is_authenticated
            and context.user.favorites.filter(pk=obj.id)
        ):
            return True
        return False
   
    def get_is_in_shopping_cart(self, obj):
        """Метод для отображения поля корзины покупок."""
        context = self.context.get('request')
        if (
            context
            and context.user.is_authenticated
            and context.user.shopping_cart.filter(pk=obj.id)
        ):
            return True
        return False

    def to_representation(self, obj):
        """Метод изменения выходных данных сериализатора."""
        self.fields.pop('ingredients')
        self.fields['tags'] = TagSerializer(many=True)
        representation = super().to_representation(obj)
        representation['id'] = obj.id
        representation['author'] = UserSerializer(obj.author).data
        representation['ingredients'] = IngredientInRecipeSerializer(
            obj.ingredients_in_recipe.all(), many=True
        ).data
        return representation

    '''def validate_ingredients(self, value):
        """Метод валидации поля ингредиентов."""
        try:
            ingredients_items = []
            for ingredient in value:
                if ingredient not in ingredients_items:
                    ingredients_items.append(ingredient)
                    Ingredient.objects.get(id=ingredient.get('ingredient_id'))
                else:
                    raise serializers.ValidationError(
                        'В рецепт добавлены повторяющиеся ингредиенты')
            return value
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError(
                'Данного ингредиента не существует'
            )
        except TypeError:
            raise serializers.ValidationError(
                'Неправильный формат данных ингредиентов'
            )'''

    def validate_tags(self, value):
        """Метод валидации поля тегов."""
        try:
            tags_items = []
            for tag in value:
                if tag not in tags_items:
                    tags_items.append(tag)
                else:
                    raise serializers.ValidationError(
                        'В рецепт добавлены повторяющиеся теги')
        except TypeError:
            raise serializers.ValidationError(
                'Неправильный формат данных тегов')
        return value

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Поле с изображением обязательно.')
        return value


class ShoppingCartSerializer(serializers.Serializer):
    """Сериализатор для списка покупок."""

    def update(self, instance, validated_data):
        """Метод добавления рецептов в корзину покупок."""
        if instance in self.context.get('request').user.shopping_cart.all():
            raise serializers.ValidationError(
                'Данный рецепт уже добавлен в корзину')
        self.context.get('request').user.shopping_cart.add(instance)
        return instance

    def to_representation(self, obj):
        """Метод представления добавленных рецептов."""
        representation = super().to_representation(obj)
        representation['id'] = obj.id
        representation['name'] = obj.name
        representation['image'] = obj.image.url
        representation['cooking_time'] = obj.cooking_time
        return representation


class FavoriteSerializer(serializers.Serializer):
    """Сериализатор для добавления рецептов в избранное."""

    def update(self, instance, validated_data):
        """Метод добавления рецептов в избранное."""
        if instance in self.context.get('request').user.favorites.all():
            raise serializers.ValidationError(
                'Данный рецепт уже добавлен в избранное')
        self.context.get('request').user.favorites.add(instance)
        return instance

    def to_representation(self, instance):
        """Метод представления добавленных рецептов."""
        return ShoppingCartSerializer(instance).data
