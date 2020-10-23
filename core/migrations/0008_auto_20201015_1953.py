# Generated by Django 3.0.7 on 2020-10-15 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_mediopago'),
    ]

    operations = [
        migrations.CreateModel(
            name='Archivo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('documento', models.FileField(upload_to='archivos/documentos/')),
            ],
            options={
                'verbose_name': 'archivo',
                'verbose_name_plural': 'archivos',
                'db_table': 'core_archivos',
            },
        ),
        migrations.AddField(
            model_name='factura',
            name='archivos',
            field=models.ManyToManyField(blank=True, to='core.Archivo'),
        ),
    ]