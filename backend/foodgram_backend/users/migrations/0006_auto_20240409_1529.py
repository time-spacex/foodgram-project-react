# Generated by Django 3.2.16 on 2024-04-09 12:29

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_customuser_is_admin'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('subscriber', 'subscribed_to'), name='unique_subscriber_and_subscribed_to'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.CheckConstraint(check=models.Q(('subscriber', django.db.models.expressions.F('subscribed_to')), _negated=True), name='prevent_self_subscription'),
        ),
    ]
