# Generated by Django 3.1.7 on 2021-05-29 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20210428_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facturaproveedor',
            name='factura',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='facturas_proveedor', to='core.factura'),
        ),
    ]