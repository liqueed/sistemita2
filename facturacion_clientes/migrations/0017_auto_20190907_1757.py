# Generated by Django 2.2.4 on 2019-09-07 20:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion_clientes', '0016_pagotarjetadecreditocorporativa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagotarjetadecreditocorporativa',
            name='monto',
        ),
        migrations.RemoveField(
            model_name='pagotarjetadecreditocorporativa',
            name='monto_currency',
        ),
    ]