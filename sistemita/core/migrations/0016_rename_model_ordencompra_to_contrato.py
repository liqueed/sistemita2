# Generated by Django 3.2 on 2023-02-22 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_add_field_porcentaje_socios'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OrdenCompra',
            new_name='Contrato',
        ),
        migrations.AlterModelOptions(
            name='contrato',
            options={'ordering': ('fecha',), 'verbose_name': 'contrato', 'verbose_name_plural': 'contratos'},
        ),
    ]