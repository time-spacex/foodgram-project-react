from django.core.management.base import BaseCommand
import os
import csv

from recipes.models import Ingredient


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        ingredients_to_create = []
        for csv_file_path in options['csv_file']:
            if os.path.exists(csv_file_path):
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        ingredient = Ingredient(
                            name=row[0],
                            measurement_unit=row[1]
                        )
                        ingredients_to_create.append(ingredient)
                    Ingredient.objects.bulk_create(ingredients_to_create)
                    self.stdout.write(self.style.SUCCESS(
                        'Ингредиенты успешно созданы в базе данных.'))
            else:
                self.stderr.write(self.style.ERROR(
                    f'Файл отсутствует: {csv_file_path}'))
