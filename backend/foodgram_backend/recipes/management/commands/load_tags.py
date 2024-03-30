import os
import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for csv_file_path in options['csv_file']:
            if os.path.exists(csv_file_path):
                with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        Tag.objects.create(
                            name=row[0],
                            color=row[1],
                            slug=row[2]
                        )
                    self.stdout.write(self.style.SUCCESS(
                        'Теги успешно созданы в базе данных.'))
            else:
                self.stderr.write(self.style.ERROR(
                    f'Файл отсутствует: {csv_file_path}'))
