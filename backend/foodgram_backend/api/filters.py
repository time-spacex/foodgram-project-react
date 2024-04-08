import django_filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(django_filters.FilterSet):
    """Кастомный фильтр для представления ингредиентов."""

    name = django_filters.CharFilter(
        field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    """Кастомный фильтр для представления рецептов."""

    tags = django_filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = django_filters.NumberFilter(
        field_name='favorites',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        field_name='shopping_cart',
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'tags',
        )

    def filter_is_favorited(self, queryset, name, value):
        """Метод обработки фильтрации избранных рецептов."""
        if value and self.request.user.is_authenticated:
            return self.request.user.favorites.all()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Метод обработки фильтрации рецептов в списке покупок."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shopping_cart__user=self.request.user)
        return queryset
