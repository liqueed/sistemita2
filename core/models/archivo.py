from django.db import models


class Archivo(models.Model):
    documento = models.FileField(upload_to='archivos/documentos/')

    def __str__(self):
        return '{}'.format(self.documento)

    class Meta:
        db_table = 'core_archivos'
        verbose_name = 'archivo'
        verbose_name_plural = 'archivos'
