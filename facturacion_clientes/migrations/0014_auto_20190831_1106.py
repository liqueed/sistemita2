# Generated by Django 2.2.4 on 2019-08-31 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion_clientes', '0013_pagoclientetransferenciaaliqueed_movimiento_bancario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagoclientetransferenciaaliqueed',
            name='movimiento_bancario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='facturacion_clientes.MovimientoBancario'),
        ),
    ]