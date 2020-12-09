from django.db import models

from core.models.utils import TimeStampedModel


class MedioPago(TimeStampedModel, models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')

    def __str__(self):
        return '{}'.format(self.nombre)

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'medio de pago'
        verbose_name_plural = 'medios de pago'
