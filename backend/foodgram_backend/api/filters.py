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

    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
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
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        )

    def filter_is_favorited(self, queryset, name, value):
        """Метод обработки фильтрации избранных рецептов."""
        if value == 1 and self.request.user.is_authenticated:
            return self.request.user.favorites.all()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Метод обработки фильтрации рецептов в списке покупок."""
        if value == 1 and self.request.user.is_authenticated:
            return self.request.user.shopping_cart.all()
        return queryset
