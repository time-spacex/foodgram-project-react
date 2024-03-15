from rest_framework import status, permissions, pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from djoser.views import UserViewSet

from users.models import CustomUser
from .serializers import SignUpSerializer, UserSerializer


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

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
