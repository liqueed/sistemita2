"""Modelos de pagos a proveedores."""

# Django
from django.db import models

# Models
from core.models.proveedor import Proveedor, FacturaProveedor
from core.models.mediopago import MedioPago
from core.models.utils import TimeStampedModel


class Pago(TimeStampedModel, models.Model):
    """Modelo pago a proveedores."""

    fecha = models.DateField(blank=False)
    proveedor = models.ForeignKey(Proveedor, blank=False, on_delete=models.CASCADE)
    total = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    class Meta:
        """Configuraciones del modelo."""

        db_table = 'accounting_proveedor_pago'
        ordering = ('creado',)
        verbose_name = 'pago'
        verbose_name_plural = 'pagos'


class PagoFactura(TimeStampedModel, models.Model):
    """Modelo Factura pago.

    Cada pago a proveedor puede tener una o muchas facturas asociadas.
    """

    pago = models.ForeignKey(Pago, blank=False, on_delete=models.CASCADE, related_name='pago_facturas')
    factura = models.ForeignKey(FacturaProveedor, blank=False, on_delete=models.CASCADE)
    ganancias = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    ingresos_brutos = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    iva = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    class Meta:
        """Configuraciones del modelo."""

        db_table = 'accounting_proveedor_pago_factura'
        verbose_name = 'factura pago'
        verbose_name_plural = 'facturas pago'


class PagoFacturaPago(models.Model):
    """Modelo de pago de facturas de pago.

    Cada factura asociada a un pago a proveedor puede tener uno o mucho métodos
    de pagos.
    """

    metodo = models.ForeignKey(MedioPago, blank=False, on_delete=models.CASCADE)
    pago_factura = models.ForeignKey(PagoFactura, blank=False, on_delete=models.CASCADE,
                                     related_name='pago_factura_pagos')
    monto = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    class Meta:
        """Configuraciones del modelo."""

        db_table = 'accounting_proveedor_pago_factura_pago'
        verbose_name = 'pago factura pago'
        verbose_name_plural = 'pagos factura pago'
