from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import SignUpSerializer


class SignUpView(APIView):
    """Вью класс регистрации пользователей."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Метод обработки 'post' запроса при регистрации пользователей."""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
