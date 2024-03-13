from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import SignUpView
# from djoser.urls.jwt import urlpatterns


urlpatterns = [
    path('users/', SignUpView.as_view(), name='signup'),
]