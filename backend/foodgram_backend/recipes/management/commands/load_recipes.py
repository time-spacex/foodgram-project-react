import os
import csv

from django.core.management.base import BaseCommand

from users.models import CustomUser
from recipes.models import Recipe


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for csv_file_path in options['csv_file']:
            if os.path.exists(csv_file_path):
                with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file, delimiter=';')
                    line_number = 1
                    for row in reader:
                        line_number += 1
                        author = CustomUser.objects.get(username=row['author_username'])
                        recipe = Recipe.objects.create(
                            name=row['name'],
                            text=row['text'],
                            cooking_time=row['cooking_time'],
                            image=row['image'],
                            author=author
                        )
                        ingredients_id = row['ingredients_id'].split(',')
                        ingredients_amount = row['ingredients_amount'].split(',')
                        try:
                            if len(ingredients_id) != len(ingredients_amount):
                                raise ValueError(
                                    'Не совпадает количество в столбце ingredients_id и '
                                    'количество значений в столбце ingredients_amount. '
                                    f'Номер строки: {line_number}'
                                )
                            for item in range(len(ingredients_id)):
                                recipe.ingredients_in_recipe.create(
                                    ingredient_id=int(ingredients_id[item]),
                                    amount=int(ingredients_amount[item])
                                )
                            tags_id = row['tags'].split(',')
                            for tag in tags_id:
                                recipe.tags.add(int(tag))
                        except ValueError as error:
                            self.stdout.write(self.style.ERROR(str(error)))
                    line_number -= 1
                    self.stdout.write(self.style.SUCCESS(
                        f'Рецепты успешно созданы, {line_number} шт'))
            else:
                self.stderr.write(self.style.ERROR(f'Отсутствует файл: {csv_file_path}'))
