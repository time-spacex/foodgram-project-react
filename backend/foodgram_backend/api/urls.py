from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, TagsViewSet, IngredientsViewSet, RecipesViewSet, RecipeEditViewSet


router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('recipes/', RecipeEditViewSet.as_view(), name='recipes_create'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]