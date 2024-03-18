import django_filters

from recipes.models import Ingredient


class IngredientFilter(django_filters.FilterSet):
    """Кастомный фильтр для представления ингредиентов."""

    name = django_filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)