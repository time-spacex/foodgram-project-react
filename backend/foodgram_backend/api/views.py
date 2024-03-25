from django.http import HttpResponse
from rest_framework import status, permissions, pagination, exceptions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from users.models import CustomUser
from recipes.models import Tag, Ingredient, Recipe
from .serializers import (
    SignUpSerializer,
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
    http_method_names = ['get', 'post']

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
            serializer = UserSerializer(page, many=True, context=request)
            return self.get_paginated_response(serializer.data)
        serializer = UserSerializer(queryset, many=True, context=request)
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
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        url_path=r'(?P<recipe_id>\d+)/shopping_cart',
        url_name='add_delete_from_sopping_cart'
    )
    def add_delete_from_sopping_cart(self, request, recipe_id):
        recipe = Recipe.objects.get(id=recipe_id)
        if self.request.method == 'POST':
            serializer = ShoppingCartSerializer(
                instance=recipe,
                data=request.data,
                context=request)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            request.user.shopping_cart.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)


'''class ShoppingCartViewSet(APIView):

    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'post', 'delete']

    def get(self, request):
        shopping_cart = request.user.shopping_cart.all()
        response = HttpResponse(
            shopping_cart,
            headers={
            "Content-Type": "application/vnd.ms-excel",
            "Content-Disposition": 'attachment; filename="foo.xls"',
            },
        )

        return Response(status=status.HTTP_200_OK)

    def post(self, request, recipe_id):
        recipe = Recipe.objects.get(id=recipe_id)
        serializer = ShoppingCartSerializer(
            instance=recipe,
            data=request.data,
            context=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)'''
