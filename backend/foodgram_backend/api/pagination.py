from collections import OrderedDict

from rest_framework.pagination import (
    PageNumberPagination as MyPageNumberPagination)
from rest_framework.response import Response

from .filters import RecipeFilter


class PageNumberPagination(MyPageNumberPagination):

    page_size_query_param = 'limit'
    page_size = 6

    def get_limit(self, request):
        """Функция для извлечения значения параметра `limit` из запроса."""
        return int(request.query_params.get(
            self.page_size_query_param, self.page_size))

    def filter_queryset(self, queryset, request):
        """Метод для применения фильтров к queryset."""
        filter_backend = RecipeFilter(
            request.query_params,
            queryset=queryset,
            request=request
        )
        return filter_backend.qs

    def paginate_queryset(self, queryset, request, view=None):
        """
        Переопределенный метод, который возвращает результаты пагинации и
        обновляет поле `count` так, чтобы оно показывало количество элементов,
        ограниченных параметром `limit`.
        """
        queryset = self.filter_queryset(queryset, request)
        self.count = queryset.count()
        self.count = min(self.get_page_size(request), self.count)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """Переопределенный метод, который возвращает ответ пагинации."""
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
