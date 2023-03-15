"""Modelo de cliente."""

# Utils
from decimal import Decimal

# Django
from django.core.validators import MaxValueValidator
from django.db import models

# Models
from sistemita.core.constants import MONEDAS
from sistemita.core.models.archivo import Archivo
from sistemita.core.models.entidad import Distrito, Localidad, Provincia
from sistemita.core.models.utils import FacturaAbstract, TimeStampedModel
from sistemita.utils.commons import get_porcentaje


class Cliente(TimeStampedModel, models.Model):
    """Modelo cliente."""

    FORMAS_ENVIO = (('C', 'Correo'), ('U', 'Link'))
    razon_social = models.CharField('Razón Social', blank=False, max_length=128)
    cuit = models.CharField('CUIT', blank=False, max_length=11, unique=True)
    correo = models.EmailField(blank=True, null=True, unique=True)
    telefono = models.CharField('Teléfono', max_length=14, blank=True)

    calle = models.CharField('Calle', max_length=35, blank=True)
    numero = models.CharField('Número', max_length=12, blank=True)
    piso = models.CharField('Piso', max_length=4, blank=True)
    dpto = models.CharField('Departamento', max_length=4, blank=True)

    provincia = models.ForeignKey(Provincia, null=True, blank=True, verbose_name='Provincia', on_delete=models.SET_NULL)
    distrito = models.ForeignKey(Distrito, null=True, blank=True, verbose_name='Distrito', on_delete=models.SET_NULL)
    localidad = models.ForeignKey(Localidad, null=True, blank=True, verbose_name='Localidad', on_delete=models.SET_NULL)

    tipo_envio_factura = models.CharField(
        blank=True,
        verbose_name='Forma de envío',
        choices=FORMAS_ENVIO,
        max_length=1,
        default='C',
    )
    link_envio_factura = models.URLField(blank=True, verbose_name='URL de envío')
    correo_envio_factura = models.EmailField(blank=True, verbose_name='Correo de envío')

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return f'{self.razon_social} - {self.cuit}'

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('razon_social',)
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'


class FacturaCategoria(TimeStampedModel):
    """Categoría de factura."""

    nombre = models.CharField(blank=False, max_length=100, unique=True)

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return f'{self.nombre}'


class Factura(FacturaAbstract):
    """Modelo factura de cliente."""

    cliente = models.ForeignKey(Cliente, blank=False, on_delete=models.CASCADE)
    archivos = models.ManyToManyField(Archivo, blank=True)
    porcentaje_fondo = models.PositiveSmallIntegerField(default=15)
    contrato = models.ForeignKey('Contrato', blank=True, null=True, on_delete=models.SET_NULL)
    categoria = models.ForeignKey(FacturaCategoria, blank=True, null=True, on_delete=models.SET_NULL)
    proveedores = models.ManyToManyField('Proveedor', blank=True)
    porcentaje_socio_alan = models.DecimalField(
        blank=False, decimal_places=2, max_digits=5, default=2.5, validators=[MaxValueValidator(100)]
    )
    porcentaje_socio_ariel = models.DecimalField(
        blank=False, decimal_places=2, max_digits=5, default=2.5, validators=[MaxValueValidator(100)]
    )

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return f'{self.fecha} - {self.numero} - {self.cliente.razon_social} - {self.moneda_monto}'

    @property
    def porcentaje_fondo_monto(self):
        """Retorno el monto del porcentaje de fondo."""
        return get_porcentaje(self.total, self.porcentaje_fondo)

    @property
    def porcentaje_fondo_neto(self):
        """Retorno el monto del porcentaje de fondo desde el monto neto."""
        return get_porcentaje(self.neto, self.porcentaje_fondo)

    @property
    def porcentaje_socios_neto(self):
        """Retorno el monto del porcentaje de socios desde el monto neto."""
        porcentaje_socios = self.porcentaje_socio_alan + self.porcentaje_socio_ariel
        return get_porcentaje(self.neto, porcentaje_socios)

    @property
    def moneda_porcentaje_fondo_monto(self):
        """Retorno el monto del porcentaje de fondo."""
        return f'{self.get_moneda_display()} {self.porcentaje_fondo_monto}'

    @property
    def monto_neto_sin_fondo(self):
        """Retorno el monto neto restado el porcentaje fondo."""
        return self.neto - round(Decimal(self.porcentaje_fondo_neto), 2)

    @property
    def moneda_monto_neto_sin_fondo(self):
        """Retorno el monto neto restado el porcentaje fondo."""
        return f'{self.get_moneda_display()} {self.monto_neto_sin_fondo}'

    @property
    def monto_neto_sin_fondo_porcentaje_socios(self):
        """Retorno el monto neto restado el porcentaje fondo y el porcentaje de socios."""
        fondo_porcentaje_socios = round(Decimal(self.porcentaje_fondo_neto) + Decimal(self.porcentaje_socios_neto), 2)
        return self.neto - fondo_porcentaje_socios

    @property
    def moneda_monto_neto_sin_fondo_porcentaje_socios(self):
        """Retorno el monto neto restado el porcentaje fondo y el porcentaje de socios."""
        return f'{self.get_moneda_display()} {self.monto_neto_sin_fondo_porcentaje_socios}'

    @property
    def status(self):
        """Retorna en el estado que está la factura para mostrar en el panel de control"""
        # send: 1
        # paid: 2
        # delayed: 3
        # done: 4
        status = 1

        # Verifica si se hizo la recepcion de todas la fc de proveedores y si fueron pagadas
        recepcion_fc_proveedores = False
        pago_a_proveedores = False
        fc_proveedores = self.factura_distribuida.factura_distribuida_proveedores.all()
        if fc_proveedores:
            fc_proveedor_realizadas = 0
            fc_proveedor_pagadas = 0

            for fc in fc_proveedores:
                if fc.factura_proveedor:
                    fc_proveedor_realizadas += 1
                    if fc.factura_proveedor.cobrado:
                        fc_proveedor_pagadas += 1

            if fc_proveedores.count() == fc_proveedor_realizadas:
                recepcion_fc_proveedores = True

            if fc_proveedores.count() == fc_proveedor_pagadas:
                pago_a_proveedores = True

        # Set de estado
        if self.factura_distribuida.distribuida and self.cobrado and recepcion_fc_proveedores and pago_a_proveedores:
            status = 4
        elif self.factura_distribuida.distribuida and not self.cobrado and recepcion_fc_proveedores:
            status = 3
        elif self.factura_distribuida.distribuida and self.cobrado and recepcion_fc_proveedores:
            status = 2

        return status

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('fecha',)
        verbose_name = 'factura'
        verbose_name_plural = 'facturas'


class Contrato(TimeStampedModel, models.Model):
    """Modelo contrato de cliente."""

    fecha_desde = models.DateField(blank=False)
    fecha_hasta = models.DateField(blank=False, null=True)
    categoria = models.ForeignKey(
        FacturaCategoria, blank=True, null=True, on_delete=models.SET_NULL, related_name='categoria_contrato'
    )
    cliente = models.ForeignKey(Cliente, blank=False, on_delete=models.CASCADE)
    proveedores = models.ManyToManyField('Proveedor', blank=True)
    detalle = models.TextField(blank=True, max_length=255)
    moneda = models.CharField(blank=False, max_length=1, choices=MONEDAS, default='P')
    monto = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    @property
    def moneda_monto(self):
        """Retorno el monto del contrato."""
        return f'{self.get_moneda_display()} {self.monto}'

    def __str__(self):
        return f'{self.fecha_desde} | {self.cliente}'

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('fecha_desde',)
        verbose_name = 'contrato'
        verbose_name_plural = 'contratos'


class FacturaImputada(TimeStampedModel, models.Model):
    """Modelo de imputación de facturas de cliente."""

    fecha = models.DateField(blank=False)
    cliente = models.ForeignKey(Cliente, blank=False, on_delete=models.CASCADE)
    facturas = models.ManyToManyField(Factura, related_name='facturas_imputacion')
    nota_de_credito = models.OneToOneField(
        Factura, blank=True, null=True, on_delete=models.SET_NULL, related_name='factura_nc'
    )
    moneda = models.CharField(blank=False, max_length=1, choices=MONEDAS, default='P')
    monto_facturas = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    monto_nota_de_credito = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    total_factura = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('-fecha',)
        verbose_name = 'factura imputada'
        verbose_name_plural = 'facturas imputadas'

    def __str__(self):
        """Representación del modelo."""
        return f'{self.fecha} | {self.cliente} | {self.total_factura}'

    def save(self, *args, **kwargs):
        """Valida que el total de la factura no sea negativo."""
        self.total_factura = max(self.total_factura, 0.0)
        return super().save(*args, **kwargs)


class FacturaDistribuida(TimeStampedModel):
    """Modelo de distribución de factura de cliente."""

    factura = models.OneToOneField(Factura, blank=False, on_delete=models.CASCADE, related_name='factura_distribuida')
    distribuida = models.BooleanField(default=False)
    monto_distribuido = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    def __str__(self):
        """Representación del modelo."""
        return f'{self.factura.numero} | {self.factura.cliente} | {self.monto_distribuido}'

    class Meta:
        """Configuraciones del modelo."""

        verbose_name = 'factura distribuida'
        verbose_name_plural = 'facturas distribuidas'

    @property
    def moneda_monto_distribuido(self):
        """Retorno el monto de la orden de compra."""
        return f'{self.factura.get_moneda_display()} {self.monto_distribuido}'
