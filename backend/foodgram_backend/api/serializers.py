from django.core.mail import send_mail
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from users.models import CustomUser, Subscription
from recipes.models import Recipe, Tag, Ingredient, IngredientsInRecipe


'''class SignUpSerializer(serializers.ModelSerializer):
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
        return data'''


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
            if (
                self.context.get('request').user.is_authenticated
                and self.context.get(
                    'request').user.id == subscriber.subscriber_id
            ):
                return True
        return False


class SubscriptionSerializer(serializers.Serializer):
    """Сериализатор для создания подписок."""

    def update(self, instance, validated_data):
        """Метод создания опдписки на пользователя."""
        if instance == self.context.get('request').user:
            raise serializers.ValidationError(
                'Невозможно оформить подписку на свой профиль.'
            )
        for subscriprion in self.context.get(
            'request'
        ).user.subscriptions.all():
            if instance == subscriprion.subscribed_to:
                raise serializers.ValidationError(
                    'Данный пользователь уже добавлен в подписки')
        Subscription.objects.create(
            subscriber=self.context.get('request').user,
            subscribed_to=instance
        )
        return instance

    def to_representation(self, instance):
        """Метод представления созданной подписки."""
        user_data = UserSerializer(
            instance=instance,
            context=self.context
        ).data
        recipe_data = FavoriteSerializer(
            instance=instance.recipes.all(),
            many=True,
            context=self.context
        ).data
        query_params = self.context.get(
            'request'
        ).query_params.get('recipes_limit')
        if query_params:
            query_params = int(query_params)
            recipe_data = recipe_data[0:query_params]
        return_data = {
            **user_data,
            'recipes': recipe_data,
            'recipes_count': len(recipe_data)
        }
        return return_data


class SubscriptionGetSerializer(serializers.Serializer):
    """Сериализатор для получения списка подписок."""

    def to_representation(self, instance):
        """Метод представления списка подписок."""
        ret = SubscriptionSerializer(
            instance,
            context=self.context,
        ).data
        return ret


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

    id = serializers.IntegerField(source='ingredient_id')

    class Meta:
        model = IngredientsInRecipe
        fields = (
            'id',
            'amount',
        )


class RecipeEditSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования рецептов."""

    ingredients = IngredientInRecipeEditSerializer(
        many=True, allow_null=False, allow_empty=False)
    image = Base64ImageField(required=True)
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

    def create(self, validated_data):
        """Метод создания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            recipe.ingredients_in_recipe.create(**ingredient)
        for tag in tags:
            recipe.tags.add(tag)
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
        """Метод поля избранных рецептов."""
        user = self.context.get('request').user
        if user.is_authenticated and user in obj.favorites.all():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        """Метод поля рецептов в корзине покупок."""
        user = self.context.get('request').user
        if user.is_authenticated and user in obj.shopping_cart.all():
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

    def validate_ingredients(self, value):
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
            )

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
