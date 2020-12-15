"""Modelo Archivo."""

# Django
from django.db import models


class Archivo(models.Model):
    """Modelo de Archivo.

    Este modelo es utilizado para cualquier archivo adjunto de otro modelo.
    """

    documento = models.FileField(upload_to='archivos/documentos/')

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return '{}'.format(self.documento)

    class Meta:
        """Configuraciones del modelo."""

        db_table = 'core_archivos'
        verbose_name = 'archivo'
        verbose_name_plural = 'archivos'
