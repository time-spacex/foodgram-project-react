# Generated by Django 3.2.16 on 2024-04-09 16:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20240409_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsinrecipe',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Количество ингредиентов не должно быть меньше 1 .'), django.core.validators.MinValueValidator(32767, message='Количество ингредиентов не должно превышать 32767 .')], verbose_name='Количество'),
        ),
    ]