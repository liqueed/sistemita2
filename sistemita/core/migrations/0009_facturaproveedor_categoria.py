# Generated by Django 3.1.7 on 2021-12-08 00:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_facturaproveedorcategoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='facturaproveedor',
            name='categoria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.facturaproveedorcategoria'),
        ),
    ]