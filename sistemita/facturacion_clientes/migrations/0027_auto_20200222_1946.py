# Generated by Django 2.2.7 on 2020-02-22 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion_clientes', '0026_auto_20200222_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facturadordeconsultor',
            name='cbu',
            field=models.CharField(max_length=22, null=True),
        ),
    ]