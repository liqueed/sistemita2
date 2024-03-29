# Generated by Django 3.1.7 on 2021-12-07 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_facturaproveedorimputada'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacturaCategoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado', models.DateTimeField(auto_now_add=True, verbose_name='creado')),
                ('modificado', models.DateTimeField(auto_now=True, verbose_name='modificado')),
                ('nombre', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'get_latest_by': 'modificado',
                'abstract': False,
            },
        ),
    ]
