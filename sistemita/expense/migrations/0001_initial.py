# Generated by Django 3.1.7 on 2021-09-30 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0002_factura_porcentaje_fondo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fondo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True, verbose_name='creado')),
                ('modificado', models.DateTimeField(auto_now=True, verbose_name='modificado')),
                ('moneda', models.CharField(choices=[('P', '$'), ('D', 'USD')], default='P', max_length=1)),
                ('monto', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('disponible', models.BooleanField(default=True)),
                ('factura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.factura')),
            ],
            options={
                'verbose_name': 'fondo',
                'verbose_name_plural': 'fondos',
                'db_table': 'expense_fondos',
                'ordering': ('creado',),
            },
        ),
        migrations.CreateModel(
            name='Costo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True, verbose_name='creado')),
                ('modificado', models.DateTimeField(auto_now=True, verbose_name='modificado')),
                ('fecha', models.DateField()),
                ('descripcion', models.CharField(max_length=500, verbose_name='descripción')),
                ('moneda', models.CharField(choices=[('P', '$'), ('D', 'USD')], default='P', max_length=1)),
                ('monto', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('fondo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='expense.fondo')),
            ],
            options={
                'verbose_name': 'gasto',
                'verbose_name_plural': 'gastos',
                'db_table': 'expense_gastos',
                'ordering': ('creado',),
            },
        ),
    ]
