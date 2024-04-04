import os
import csv

from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from users.models import CustomUser


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for csv_file_path in options['csv_file']:
            if os.path.exists(csv_file_path):
                with open(csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row[5] != 'True':
                            user = CustomUser.objects.create_user(
                                username=row[0],
                                first_name=row[1],
                                last_name=row[2],
                                email=row[3],
                                password=row[4]
                            )
                        elif row[5] == 'True':
                            user = CustomUser.objects.create_superuser(
                                username=row[0],
                                first_name=row[1],
                                last_name=row[2],
                                email=row[3],
                                password=row[4]
                            )
                        Token.objects.get_or_create(user=user)
                    self.stdout.write(self.style.SUCCESS(
                        'Пользователи успешно созданы в базе данных.'))
            else:
                self.stderr.write(self.style.ERROR(
                    f'Файл отсутствует: {csv_file_path}'))
