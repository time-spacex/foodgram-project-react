from django.http import HttpResponse
from django.db.models import Sum
from rest_framework import (
    status, permissions, pagination, exceptions, viewsets, serializers)
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from users.models import CustomUser
from recipes.models import IngredientsInRecipe, Tag, Ingredient, Recipe
from .serializers import (
    FavoriteSerializer,
    SignUpSerializer,
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


class CustomUserViewSet(UserViewSet):
    """Представление для работы с пользователями."""

    permission_classes = (permissions.AllowAny,)
    pagination_class = pagination.LimitOffsetPagination
    http_method_names = ['get', 'post', 'delete']

    def create(self, request):
        """Метод API для создания новых пользователей."""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """Метод API получения queryset пользователей."""
        return CustomUser.objects.all()

    def list(self, request):
        """Метод API представления списка пользователей."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = UserSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = UserSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Метод API для представления пользователя."""
        instance = self.get_object()
        serializer = UserSerializer(instance)
        return Response(serializer.data)

    def get_instance(self):
        """Метод API для возврата объекта пользователя в запросе."""
        if self.request.user.is_authenticated:
            return self.request.user
        raise exceptions.AuthenticationFailed()

    @action(
        detail=False,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path=r'(?P<user_id>\d+)/subscribe',
        url_name='add_delete_subscription',
    )
    def subscribe(self, request, user_id):
        """Метод создания и удаления подписок."""
        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if self.request.method == 'POST':
            serializer = SubscriptionSerializer(
                instance=user,
                data=request.data,
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
        pagination_class = pagination.LimitOffsetPagination,
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
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Метод для получения сериализатора."""
        if self.request.method in self.http_edit_methodes:
            return RecipeEditSerializer
        return super().get_serializer_class()
    
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
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            if self.request.method == 'POST':
                raise serializers.ValidationError(
                    'Данного рецепта не существует.')
            return Response(status=status.HTTP_404_NOT_FOUND)
        if self.request.method == 'POST':
            serializer = ShoppingCartSerializer(
                instance=recipe,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            if recipe not in request.user.shopping_cart.all():
                raise serializers.ValidationError(
                    'Данный рецепт не был добавлен в корзину покупок')
            request.user.shopping_cart.remove(recipe)
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
            ingredient = Ingredient.objects.get(pk=buy_item.get('ingredient_id'))
            purchase_data += (
                ingredient.name + ', '
                + str(buy_item.get('buy_amount'))
                + ' ' + ingredient.measurement_unit + '; '
            )
        response = HttpResponse(
            purchase_data,
            headers={
            'Content-Type': 'text/plain',
            'Content-Disposition': 'attachment; filename="purchase_list.txt"',
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
        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError('Данного рецепта не существует.')
        if self.request.method == 'POST':
            serializer = FavoriteSerializer(
                instance=recipe,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            request.user.favorites.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
