from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import (
    status, permissions, viewsets, serializers)
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from users.models import CustomUser, Subscription
from recipes.models import (
    Favorites,
    IngredientsInRecipe, ShoppingCart, Tag, Ingredient, Recipe)
from .serializers import (
    FavoriteSerializer,
    SubscriptionGetSerializer,
    SubscriptionSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    UserSerializer, RecipeEditSerializer, ShoppingCartSerializer
)
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminAuthorOrReadOnly
from .pagination import PageNumberPagination


class CustomUserViewSet(UserViewSet):
    """Представление для работы с пользователями."""

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        """Метод пользовательских разрешений для представлений."""
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=False,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path=r'(?P<user_id>\d+)/subscribe',
        url_name='add_delete_subscription',
    )
    def subscribe(self, request, user_id):
        """Метод создания и удаления подписок."""

        user = get_object_or_404(CustomUser, pk=user_id)
        data = {'subscriber': request.user.id, 'subscribed_to': user.id}
        if self.request.method == 'POST':
            serializer = SubscriptionSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            if not request.user.subscriptions.exists():
                raise serializers.ValidationError(
                    'У данного пользователя нет подписок')
            Subscription.objects.filter(
                subscriber=request.user,
                subscribed_to=user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path='subscriptions',
        url_name='get_subscriptions',
    )
    def get_subscriptions(self, request):
        """Метод получения списка подписок."""
        subscribed_to_queryset = CustomUser.objects.filter(
            id__in=(
                request.user.subscriptions.all().values('subscribed_to')
            )
        )
        queryset = self.filter_queryset(subscribed_to_queryset)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionGetSerializer(
            page,
            context={'request': request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipesViewSet(viewsets.ModelViewSet):
    """Представление для рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAdminAuthorOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Метод для получения сериализатора."""
        if self.action not in permissions.SAFE_METHODS:
            return RecipeEditSerializer
        return RecipeSerializer

    @action(
        detail=False,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path=r'(?P<recipe_id>\d+)/shopping_cart',
        url_name='add_delete_from_sopping_cart'
    )
    def add_delete_from_sopping_cart(self, request, recipe_id):
        """Метод добавления и удаления рецептов в корзину покупок."""
        if self.request.method == 'POST':
            data = {
                'user': self.request.user.id,
                'recipe': recipe_id
            }
            serializer = ShoppingCartSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            shopping_cart = ShoppingCart.objects.filter(
                recipe=recipe,
                user=self.request.user
            )
            if not shopping_cart.exists():
                raise serializers.ValidationError(
                    'Данный рецепт не был добавлен в корзину покупок')
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart'
    )
    def download_from_shopping_cart(self, request):
        """Метод получения списка покупок."""
        shopping_cart = ShoppingCart.objects.filter(
            user=request.user).values('recipe')
        recipes_ids = [id['recipe'] for id in shopping_cart]
        purchase = IngredientsInRecipe.objects.filter(
            recipe_id__in=recipes_ids,
        ).values('ingredient_id').annotate(buy_amount=Sum('amount'))
        purchase_data = 'Ваш список покупок: '
        for buy_item in purchase:
            ingredient = Ingredient.objects.get(
                pk=buy_item.get('ingredient_id'))
            purchase_data += (
                ingredient.name + ', '
                + str(buy_item.get('buy_amount'))
                + ' ' + ingredient.measurement_unit + '; '
            )
        response = HttpResponse(
            purchase_data,
            headers={
                'Content-Type': 'text/plain',
                'Content-Disposition': (
                    'attachment; filename="purchase_list.txt"'),
            },
        )
        return response

    @action(
        detail=False,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path=r'(?P<recipe_id>\d+)/favorite',
        url_name='add_delete_from_favorites'
    )
    def add_delete_from_favorites(self, request, recipe_id):
        """Метод для добавления и удаления рецепта в избранное."""
        if self.request.method == 'POST':
            data = {
                'user': self.request.user.id,
                'recipe': recipe_id
            }
            serializer = FavoriteSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            favorites = Favorites.objects.filter(
                recipe=recipe,
                user=self.request.user
            )
            if not favorites.exists():
                raise serializers.ValidationError(
                    'Данный рецепт не был добавлен в кизбранное')
            favorites.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
