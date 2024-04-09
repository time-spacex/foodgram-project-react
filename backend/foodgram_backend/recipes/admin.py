from django.contrib import admin

from .models import (
    Favorites,
    Recipe,
    Ingredient, IngredientsInRecipe, ShoppingCart, Tag)


class TagAdmin(admin.ModelAdmin):
    """Административная конфигурация для тегов."""
    list_display = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    """Административная конфигурация для ингредиентов."""

    list_display = ('name', 'measurement_unit')
    list_per_page = 25
    search_fields = ('name',)


class IngredientsInRecipeInline(admin.TabularInline):
    """Поле добавления ингредиентов в админке рецептов."""
    model = IngredientsInRecipe
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    """Административная конфигурация для рецептов."""

    list_display = (
        'pub_date',
        'author',
        'name',
        'tags_list'
    )
    search_fields = ('name', 'author__username', 'tags__name')
    list_display_links = ('name', 'author')
    readonly_fields = ('favorites_count',)
    inlines = [IngredientsInRecipeInline]

    def tags_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    def favorites_count(self, obj):
        return obj.favorites.count()

    favorites_count.short_description = (
        "Добавлено в избранное кол-во раз: ")


class IngredientsInRecipeAdmin(admin.ModelAdmin):
    """Административная конфигурация для ингредиентов в рецепте."""

    list_display = (
        'recipe',
        'ingredient',
        'amount'
    )
    list_per_page = 25


class ShoppingCartAdmin(admin.ModelAdmin):
    """Административная конфигурация для корзины покупок."""

    list_display = ('user', 'recipe')


class FavoritesAdmin(admin.ModelAdmin):
    """Административная конфигурация для избранных рецептов."""

    list_display = ('user', 'recipe')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorites, FavoritesAdmin)
