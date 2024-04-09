# Generated by Django 3.2.16 on 2024-04-09 12:29

import colorfield.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20240409_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsinrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Количество ингредиентов не должно быть меньше 32767 мин.'), django.core.validators.MinValueValidator(32767, message='Количество ингредиентов не должно превышать 32767 мин.')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время приготовления не должно быть меньше 32767 мин.'), django.core.validators.MaxValueValidator(32767, message='Время приготовления не должно превышать 32767 мин.')], verbose_name='Время приготовления (мин.)'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#00FF00', image_field=None, max_length=25, samples=None, unique=True, verbose_name='Цвет'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Наименование тега'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, verbose_name='Слаг'),
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingredient'),
        ),
    ]
