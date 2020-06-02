from django.db import models


class TimeStampedModel(models.Model):
    """
    TimeStampedModel

    An abstract base class model that provides self-managed "created" and "modified" fields.
    """
    creado = models.DateTimeField('Creado', editable=False, blank=True, auto_now_add=True)
    modificado = models.DateTimeField('Modificado', editable=False, blank=True, auto_now=True)

    class Meta:
        get_latest_by = 'modificado'
        abstract = True


class Cliente(TimeStampedModel, models.Model):
    nombre = models.CharField('Nombre', blank=False, null=False, max_length=128)

    class Meta:
        ordering = ('nombre', )
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'
