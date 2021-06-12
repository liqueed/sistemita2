# Generated by Django 3.1.7 on 2021-05-29 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20210529_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='factura',
            name='numero',
            field=models.CharField(max_length=20, unique=True, verbose_name='Número'),
        ),
        migrations.AlterField(
            model_name='facturaproveedor',
            name='numero',
            field=models.CharField(max_length=20, unique=True, verbose_name='Número'),
        ),
    ]