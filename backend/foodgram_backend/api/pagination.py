from rest_framework.pagination import (
    PageNumberPagination as MyPageNumberPagination)


class PageNumberPagination(MyPageNumberPagination):

    page_size_query_param = 'limit'
    page_size = 6
