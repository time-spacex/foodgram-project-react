from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import (
    status, permissions, exceptions, viewsets, serializers)
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from users.models import CustomUser
from recipes.models import Favorites, IngredientsInRecipe, ShoppingCart, Tag, Ingredient, Recipe
from .serializers import (
    FavoriteSerializer,
    # SignUpSerializer,
    SubscriptionGetSerializer,
    SubscriptionSerializer,
    UserSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeEditSerializer,
    ShoppingCartSerializer
)
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminAuthorOrReadOnly
from .pagination import PageNumberPagination


class CustomUserViewSet(UserViewSet):
    """Представление для работы с пользователями."""

    # queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        """Метод API получения queryset пользователей."""
        # нужно оставить этот метод так как метод в библиотеке 
        # djoser перезаписывает queryset = queryset.filter(pk=user.pk)
        return CustomUser.objects.all()

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().me(request, *args, **kwargs)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

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
            if not request.user.subscriptions.all():
                raise serializers.ValidationError(
                    'У данного пользователя нет подписок')
            for subscriprion in request.user.subscriptions.all():
                if subscriprion.subscribed_to == user:
                    subscriprion.delete()
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
        if page is not None:
            serializer = SubscriptionGetSerializer(
                page,
                context={'request': request},
                many=True
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionGetSerializer(
            subscribed_to_queryset,
            context={'request': request},
            many=True
        )
        return Response(serializer.data)


class TagsViewSet(viewsets.ModelViewSet):
    """Представление для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientsViewSet(viewsets.ModelViewSet):
    """Представление для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    http_method_names = ['get']
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
    http_edit_methodes = ['POST', 'PATCH', 'DELETE']
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Метод для получения сериализатора."""
        if self.request.method in self.http_edit_methodes:
            return RecipeEditSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """Метод сохранения рецепта."""
        serializer.save(author=self.request.user)

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
        shopping_cart = request.user.shopping_cart.all()
        recipes_ids = [recipe.id for recipe in shopping_cart]
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
