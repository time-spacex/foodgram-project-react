from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from colorfield import fields

from users.models import CustomUser
from foodgram_backend.constants import (
    MAX_ACCEPTABLE_VALUE,
    MAX_RECIPES_CHARFIELD_LENGTH,
    MIN_ACCEPTABLE_VALUE
)


User = get_user_model()


class Tag(models.Model):
    """Модель тегов к рецептам."""

    name = models.CharField(
        verbose_name='Наименование тега',
        max_length=MAX_RECIPES_CHARFIELD_LENGTH,
        unique=True
    )
    color = fields.ColorField(
        verbose_name='Цвет',
        default='#00FF00',
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=MAX_RECIPES_CHARFIELD_LENGTH
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
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient'
            ),
        )

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
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (мин.)',
        validators=[
            MinValueValidator(
                MIN_ACCEPTABLE_VALUE,
                message=(
                    'Время приготовления не должно '
                    f'быть меньше {MIN_ACCEPTABLE_VALUE} мин.'
                )
            ),
            MaxValueValidator(
                MAX_ACCEPTABLE_VALUE,
                message=(
                    'Время приготовления не должно '
                    f'превышать {MAX_ACCEPTABLE_VALUE} мин.'
                )
            )
        ]
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
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

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
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_ACCEPTABLE_VALUE,
                message=(
                    'Количество ингредиентов не должно '
                    f'быть меньше {MIN_ACCEPTABLE_VALUE} .'
                )
            ),
            MaxValueValidator(
                MAX_ACCEPTABLE_VALUE,
                message=(
                    'Количество ингредиентов не должно '
                    f'превышать {MAX_ACCEPTABLE_VALUE} .'
                )
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.ingredient.name} в рецепте "{self.recipe}"'


class UserRecipeRelatedModel(models.Model):
    """Модель для связи рецептов с пользователями."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True


class ShoppingCart(UserRecipeRelatedModel):
    """Модель корзины покупок."""

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'

    def __str__(self):
        return f'Рецепт {self.recipe} в корзине {self.user}'


class Favorites(UserRecipeRelatedModel):
    """Модель избранных рецептов."""

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'

    def __str__(self):
        return f'Рецепт {self.recipe} в избранных {self.user}'
