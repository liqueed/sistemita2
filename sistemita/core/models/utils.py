"""Modelos utiles para utilizar en otros modelos."""

# Django
from django.db import models

# Constantes
from sistemita.core.constants import MONEDAS, TIPOS_FACTURA


class TimeStampedModel(models.Model):
    """Modelo TimeStamped.

    Agrega al modelo los atributos para obtener cuando fue creado y modificado el objecto.
    """

    creado = models.DateTimeField('creado', editable=False, blank=True, auto_now_add=True)
    modificado = models.DateTimeField('modificado', editable=False, blank=True, auto_now=True)

    class Meta:
        """Configuraciones del modelo."""

        get_latest_by = 'modificado'
        abstract = True


class FacturaAbstract(TimeStampedModel, models.Model):
    """Clase abstracta de facturas."""

    numero = models.CharField('número', max_length=20, blank=False)
    fecha = models.DateField(blank=False)
    detalle = models.TextField(blank=True)
    tipo = models.CharField(blank=False, max_length=8, choices=TIPOS_FACTURA, default='A')

    moneda = models.CharField(blank=False, max_length=1, choices=MONEDAS, default='P')
    neto = models.DecimalField(blank=True, decimal_places=2, max_digits=12, default=0.0)
    iva = models.PositiveSmallIntegerField(blank=False, default=21)
    total = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    cobrado = models.BooleanField(default=False)
    monto_imputado = models.DecimalField(blank=True, decimal_places=2, max_digits=12, default=0.0)

    @property
    def moneda_monto(self):
        """Retorna el total y su moneda."""
        return f'{self.get_moneda_display()} {self.total}'

    def get_tipo(self):
        """Retorna tipo de factura."""
        tipo = self.tipo
        tipos = dict(TIPOS_FACTURA)
        return tipos.get(tipo)

    @property
    def total_sin_imputar(self):
        """Retorna el total y su moneda."""
        return self.total + self.monto_imputado

    class Meta:
        """Configuraciones del modelo."""

        abstract = True
