from django.contrib import admin

from .models import Recipe, Ingredient, IngredientsInRecipe, Tag


class TagAdmin(admin.ModelAdmin):
    """Административная конфигурация для тегов."""
    list_display = ('name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    """Административная конфигурация для ингредиентов."""

    list_display = ('name', 'measurement_unit')
    list_per_page = 25
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    """Административная конфигурация для рецептов."""

    list_display = (
        'author',
        'name',
        'tags_list'
    )
    search_fields = ('name', 'author__username', 'tags__name')
    list_display_links = ('name', 'author')
    readonly_fields = ('favorites_count',)

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


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientsInRecipe, IngredientsInRecipeAdmin)
