from rest_framework import status, permissions, pagination
from rest_framework.views import APIView
from rest_framework.response import Response
from djoser.views import UserViewSet

from users.models import CustomUser
from .serializers import SignUpSerializer, UserSerializer


class CustomUserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    pagination_class = pagination.LimitOffsetPagination

    def create(self, request):
        """Метод для создания новых пользователей."""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """Метод получения queryset пользователей."""
        return CustomUser.objects.all()

    def list(self, request):
        """Метод представления сериализованного списка пользователей."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)