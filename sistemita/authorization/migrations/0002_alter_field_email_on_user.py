# Generated by Django 3.1.7 on 2022-02-15 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'Este email ya está en uso.'}, max_length=254, unique=True, verbose_name='email'),
        ),
    ]
