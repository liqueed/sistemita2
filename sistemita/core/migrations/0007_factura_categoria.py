# Generated by Django 3.1.7 on 2021-12-07 22:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_facturacategoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='factura',
            name='categoria',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.facturacategoria'),
        ),
    ]
