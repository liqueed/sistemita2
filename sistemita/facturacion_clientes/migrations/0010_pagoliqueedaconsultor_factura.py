# Generated by Django 2.2.4 on 2019-08-23 23:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion_clientes', '0009_pagoliqueedaconsultor'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagoliqueedaconsultor',
            name='factura',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='facturacion_clientes.FacturaCliente'),
            preserve_default=False,
        ),
    ]