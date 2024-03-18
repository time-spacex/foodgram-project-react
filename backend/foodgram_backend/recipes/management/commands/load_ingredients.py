from django.core.management.base import BaseCommand
import os
import csv

from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for csv_file_path in options['csv_file']:
            if os.path.exists(csv_file_path):
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        Ingredient.objects.create(
                            name=row[0],
                            measurement_unit=row[1]
                        )
                    self.stdout.write(self.style.WARNING(f'Ingredients table successfuly created'))
            else:
                self.stderr.write(self.style.ERROR(f'File does not exist: {csv_file_path}'))
