# Generated by Django 2.2.7 on 2019-11-09 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion_clientes', '0024_auto_20191109_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagoliqueedaconsultor',
            name='facturador',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='facturacion_clientes.FacturadorDeConsultor'),
            preserve_default=False,
        ),
    ]