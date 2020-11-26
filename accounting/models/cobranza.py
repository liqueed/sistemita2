"""Modelos de cobranzas"""

# Django
from django.db import models

# Models
from core.models.cliente import Cliente, Factura
from core.models.mediopago import MedioPago
from core.models.utils import TimeStampedModel


class Cobranza(TimeStampedModel, models.Model):
    """Modelo cobraza a clientes"""
    cliente = models.ForeignKey(Cliente, blank=False, on_delete=models.CASCADE)
    total = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    class Meta:
        """Meta class."""
        db_table = 'accounting_cliente_cobranza'
        ordering = ('creado',)
        verbose_name = 'cobranza'
        verbose_name_plural = 'cobranzas'


class PagoFacturaCobranza(models.Model):
    """Modelo de pago de facturas cobranza."""
    metodo = models.ForeignKey(MedioPago, blank=False, on_delete=models.CASCADE)
    monto = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    class Meta:
        """Meta class."""
        db_table = 'accounting_cliente_pago_factura_cobranza'
        verbose_name = 'pago factura cobranza'
        verbose_name_plural = 'pagos factura cobranza'


class FacturaCobranza(TimeStampedModel, models.Model):
    """Modelo Factura Cobranza."""
    cobranza = models.ForeignKey(Cobranza, blank=False, on_delete=models.CASCADE)
    factura = models.ForeignKey(Factura, blank=False, on_delete=models.CASCADE)
    pago = models.ForeignKey(PagoFacturaCobranza, blank=False, on_delete=models.CASCADE)
    ganancias = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    ingresos_brutos = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    iva = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    class Meta:
        """Meta class."""
        db_table = 'accounting_cliente_factura_cobranza'
        verbose_name = 'factura cobranza'
        verbose_name_plural = 'facturas cobranza'
