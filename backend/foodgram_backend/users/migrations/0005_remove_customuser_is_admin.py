# Generated by Django 3.2.16 on 2024-04-04 10:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_customuser_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_admin',
        ),
    ]
