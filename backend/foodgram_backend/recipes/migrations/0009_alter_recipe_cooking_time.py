# Generated by Django 3.2.16 on 2024-04-09 16:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_alter_ingredientsinrecipe_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время приготовления не должно быть меньше 1 мин.'), django.core.validators.MaxValueValidator(32767, message='Время приготовления не должно превышать 32767 мин.')], verbose_name='Время приготовления (мин.)'),
        ),
    ]
