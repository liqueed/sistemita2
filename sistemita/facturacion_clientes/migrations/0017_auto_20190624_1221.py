# Generated by Django 2.2.2 on 2019-06-24 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion_clientes', '0016_auto_20190624_1145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deudacliente',
            name='cliente',
        ),
        migrations.AddField(
            model_name='deudacliente',
            name='factura',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='facturacion_clientes.FacturaCliente'),
            preserve_default=False,
        ),
    ]
