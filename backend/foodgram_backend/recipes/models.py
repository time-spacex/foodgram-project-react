from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator

from users.models import CustomUser
from foodgram_backend.settings import MAX_RECIPES_CHARFIELD_LENGTH, MAX_COLORFIELD_LENGTH, MIN_ACCEPTABLE_VALUE


User = get_user_model()


class Tag(models.Model):
    """Модель тэгов к рецептам."""

    name = models.CharField(
        verbose_name='Наименование тэга',
        max_length=MAX_RECIPES_CHARFIELD_LENGTH
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=MAX_COLORFIELD_LENGTH
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=MAX_COLORFIELD_LENGTH,
        validators=[UnicodeUsernameValidator]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_RECIPES_CHARFIELD_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=MAX_RECIPES_CHARFIELD_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_RECIPES_CHARFIELD_LENGTH
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=[MinValueValidator(
            MIN_ACCEPTABLE_VALUE,
        )]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsInRecipe',
        verbose_name='Список ингредиентов'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Список тегов')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Aвтор рецепта',
        related_name='recipes'
    )
    favorites = models.ManyToManyField(
        CustomUser,
        verbose_name='Избранное',
        blank=True,
        related_name='favorites'
    )
    shopping_cart = models.ManyToManyField(
        CustomUser,
        verbose_name='Список покупок',
        blank=True,
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    """Модель ингредиентов и их количества в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.RESTRICT,
        related_name='ingredients'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(
            MIN_ACCEPTABLE_VALUE,
        )]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient.name} в рецепте "{self.recipe}"'
