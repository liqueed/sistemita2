# Generated by Django 3.1.7 on 2021-09-17 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pago',
            name='pagado',
            field=models.BooleanField(default=True),
        ),
    ]