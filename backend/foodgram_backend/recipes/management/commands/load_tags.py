from django.core.management.base import BaseCommand
import os
import csv

from recipes.models import Tag


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for csv_file_path in options['csv_file']:
            if os.path.exists(csv_file_path):
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        Tag.objects.create(
                            name=row[0],
                            color=row[1],
                            slug=row[2]
                        )
                    self.stdout.write(self.style.SUCCESS(f'Tags in database successfuly created'))
            else:
                self.stderr.write(self.style.ERROR(f'File does not exist: {csv_file_path}'))