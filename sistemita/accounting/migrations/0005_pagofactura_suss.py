# Generated by Django 3.1.7 on 2021-11-11 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0004_pago_moneda'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagofactura',
            name='suss',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
    ]
