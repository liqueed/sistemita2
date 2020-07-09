# Generated by Django 3.0.7 on 2020-07-09 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True, verbose_name='Creado')),
                ('modificado', models.DateTimeField(auto_now=True, verbose_name='Modificado')),
                ('razon_social', models.CharField(max_length=128, verbose_name='Razón Social')),
                ('cuit', models.CharField(max_length=11, verbose_name='CUIT')),
                ('correo', models.EmailField(max_length=254)),
                ('calle', models.CharField(blank=True, max_length=35, verbose_name='Calle')),
                ('numero', models.CharField(blank=True, max_length=12, verbose_name='Número')),
                ('piso', models.CharField(blank=True, max_length=4, verbose_name='Piso')),
                ('dpto', models.CharField(blank=True, max_length=4, verbose_name='Departamento')),
                ('cbu', models.CharField(blank=True, max_length=22, null=True, verbose_name='CBU')),
                ('distrito', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Distrito', verbose_name='Distrito')),
                ('localidad', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Localidad', verbose_name='Localidad')),
                ('provincia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Provincia', verbose_name='Provincia')),
            ],
            options={
                'verbose_name': 'proveedor',
                'verbose_name_plural': 'proveedores',
                'ordering': ('razon_social',),
            },
        ),
    ]