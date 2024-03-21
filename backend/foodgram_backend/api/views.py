from rest_framework import status, permissions, pagination, exceptions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes, api_view
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from users.models import CustomUser
from recipes.models import Tag, Ingredient, Recipe
from .serializers import SignUpSerializer, UserSerializer, TagSerializer, IngredientSerializer, RecipeSerializer, RecipeEditSerializer
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

    '''def perform_create(self, serializer):
        return serializer.save(author=self.request.user)'''
