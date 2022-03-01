"""Modelo de cliente."""

# Django
from django.db import models

# Utils
from sistemita.core.constants import MONEDAS

# Models
from sistemita.core.models.archivo import Archivo
from sistemita.core.models.entidad import Distrito, Localidad, Provincia
from sistemita.core.models.utils import FacturaAbstract, TimeStampedModel


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
    categoria = models.ForeignKey(FacturaCategoria, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return f'{self.fecha} - {self.numero} - {self.cliente.razon_social} - {self.moneda_monto}'

    @property
    def porcentaje_fondo_monto(self):
        """Retorno el monto del porcentaje de fondo."""
        return round(float(self.total) * self.porcentaje_fondo / 100, 2)

    @property
    def moneda_porcentaje_fondo_monto(self):
        """Retorno el monto del porcentaje de fondo."""
        return f'{self.get_moneda_display()} {self.porcentaje_fondo_monto}'

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('fecha',)
        verbose_name = 'factura'
        verbose_name_plural = 'facturas'


class OrdenCompra(TimeStampedModel, models.Model):
    """Modelo orden de compra del cliente."""

    fecha = models.DateField(blank=False)
    cliente = models.ForeignKey(Cliente, blank=False, on_delete=models.CASCADE)
    moneda = models.CharField(blank=False, max_length=1, choices=MONEDAS, default='P')
    monto = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    @property
    def moneda_monto(self):
        """Retorno el monto de la orden de compra."""
        return f'{self.get_moneda_display()} {self.monto}'

    def __str__(self):
        return f'{self.fecha} | {self.cliente}'

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('fecha',)
        verbose_name = 'orden de compra'
        verbose_name_plural = 'ordenes de compras'


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
