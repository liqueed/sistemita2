# Generated by Django 3.1.7 on 2022-03-03 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fondo',
            options={'ordering': ('-factura__fecha',), 'verbose_name': 'fondo', 'verbose_name_plural': 'fondos'},
        ),
    ]
