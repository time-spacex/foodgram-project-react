from rest_framework.pagination import (
    PageNumberPagination as MyPageNumberPagination)

from foodgram_backend.settings import PAGE_SIZE


class PageNumberPagination(MyPageNumberPagination):

    page_size_query_param = 'limit'
    page_size = PAGE_SIZE
