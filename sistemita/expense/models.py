"""Modelos de fondos y costos."""

# Django
from django.db import models

# Sistemita
from sistemita.core.constants import MONEDAS
from sistemita.core.models.utils import TimeStampedModel


class Fondo(TimeStampedModel):
    """Modelo de fondos."""

    factura = models.ForeignKey('core.Factura', blank=False, on_delete=models.CASCADE, related_name='factura_fondo')
    moneda = models.CharField(blank=False, max_length=1, choices=MONEDAS, default='P')
    monto = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    monto_disponible = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    disponible = models.BooleanField(default=False)

    @property
    def moneda_monto(self):
        """Retorna la moneda y el monto."""
        return f'{self.get_moneda_display()} {self.monto}'

    @property
    def moneda_monto_disponible(self):
        """Retorna la moneda y el monto."""
        return f'{self.get_moneda_display()} {self.monto_disponible}'

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return (
            f'{self.factura.fecha} - {self.factura.numero} - {self.factura.cliente.razon_social} - '
            f'{self.moneda_monto} | {self.moneda_monto_disponible}'
        )

    class Meta:
        """Configuraciones del modelo."""

        db_table = 'expense_fondos'
        ordering = ('-factura__fecha',)
        verbose_name = 'fondo'
        verbose_name_plural = 'fondos'


class Costo(TimeStampedModel):
    """Modelo de costos."""

    fecha = models.DateField(blank=False)
    descripcion = models.CharField('descripción', blank=False, max_length=500)
    fondo = models.ForeignKey(Fondo, blank=False, on_delete=models.CASCADE, related_name='costos')
    moneda = models.CharField(blank=False, max_length=1, choices=MONEDAS, default='P')
    monto = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    @property
    def moneda_monto(self):
        """Retorna la moneda y el monto."""
        return f'{self.get_moneda_display()} {self.monto}'

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return f'{self.fecha} | {self.monto}'

    class Meta:
        """Configuraciones del modelo."""

        db_table = 'expense_costos'
        ordering = ('creado',)
        verbose_name = 'costo'
        verbose_name_plural = 'costos'
