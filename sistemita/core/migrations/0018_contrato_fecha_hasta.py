# Generated by Django 3.2 on 2023-02-22 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_rename_field_fecha_to_fecha_desde'),
    ]

    operations = [
        migrations.AddField(
            model_name='contrato',
            name='fecha_hasta',
            field=models.DateField(null=True),
        ),
    ]
