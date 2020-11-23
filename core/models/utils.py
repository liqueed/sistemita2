from django.db import models

from core.constants import MONEDAS


class TimeStampedModel(models.Model):
    creado = models.DateTimeField('Creado', editable=False, blank=True, auto_now_add=True)
    modificado = models.DateTimeField('Modificado', editable=False, blank=True, auto_now=True)

    class Meta:
        get_latest_by = 'modificado'
        abstract = True


class FacturaAbstract(TimeStampedModel, models.Model):
    """Clase abstracta de facturas."""
    TIPOS_FACTURA = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('NCA', 'NC A'),
        ('NCB', 'NC B'),
        ('FCPYME', 'FC PYME'),
        ('NCFCPYME', 'NC FCPYME'),
    )

    numero = models.CharField('Número', max_length=20, blank=True)
    fecha = models.DateField(blank=False)
    detalle = models.TextField(blank=True)
    tipo = models.CharField(blank=False, max_length=8, choices=TIPOS_FACTURA, default='A')

    moneda = models.CharField(blank=False, max_length=1, choices=MONEDAS, default='P')
    neto = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    iva = models.PositiveSmallIntegerField(blank=False, default=21)
    total = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    cobrado = models.BooleanField(default=False)

    @property
    def moneda_monto(self):
        return f'{self.get_moneda_display()} {self.total}'

    class Meta:
        abstract = True
