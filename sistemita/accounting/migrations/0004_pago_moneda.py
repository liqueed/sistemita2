# Generated by Django 3.1.7 on 2021-11-09 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_cobranza_moneda'),
    ]

    operations = [
        migrations.AddField(
            model_name='pago',
            name='moneda',
            field=models.CharField(choices=[('P', '$'), ('D', 'USD')], default='P', max_length=1),
        ),
    ]
