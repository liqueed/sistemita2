"""Modelo medio de pago."""

# Django
from django.db import models

# Models
from sistemita.core.models.utils import TimeStampedModel


class MedioPago(TimeStampedModel, models.Model):
    """Modelo de medio de pago."""

    nombre = models.CharField(max_length=150, verbose_name='Nombre', unique=True)

    def __str__(self):
        """Devuelve un representación legible del modelo."""
        return '{}'.format(self.nombre)

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('nombre',)
        verbose_name = 'medio de pago'
        verbose_name_plural = 'medios de pago'
