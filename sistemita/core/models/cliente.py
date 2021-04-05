"""Modelo de cliente."""

# Django
from django.db import models

# Models
from core.models.archivo import Archivo
from core.models.entidad import Provincia, Distrito, Localidad
from core.models.utils import TimeStampedModel, FacturaAbstract

# Utils
from core.constants import MONEDAS


class Cliente(TimeStampedModel, models.Model):
    """Modelo cliente."""

    FORMAS_ENVIO = (
        ('C', 'Correo'),
        ('U', 'Link')
    )
    razon_social = models.CharField('Razón Social', blank=False, null=False, max_length=128)
    cuit = models.CharField('CUIT', blank=False, null=False, max_length=11, unique=True)
    correo = models.EmailField(blank=False)
    telefono = models.CharField('Teléfono', max_length=14)

    calle = models.CharField('Calle', max_length=35, blank=True)
    numero = models.CharField('Número', max_length=12, blank=True)
    piso = models.CharField('Piso', max_length=4, blank=True)
    dpto = models.CharField('Departamento', max_length=4, blank=True)

    provincia = models.ForeignKey(Provincia, null=True, blank=True, verbose_name='Provincia', on_delete=models.SET_NULL)
    distrito = models.ForeignKey(Distrito, null=True, blank=True, verbose_name='Distrito', on_delete=models.SET_NULL)
    localidad = models.ForeignKey(Localidad, null=True, blank=True, verbose_name='Localidad', on_delete=models.SET_NULL)

    tipo_envio_factura = models.CharField(
        blank=False,
        verbose_name='Forma de envío',
        choices=FORMAS_ENVIO,
        max_length=1,
        default='C'
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


class Factura(FacturaAbstract):
    """Modelo factura de cliente."""

    cliente = models.ForeignKey(Cliente, blank=False, on_delete=models.CASCADE)
    archivos = models.ManyToManyField(Archivo, blank=True)

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return '{} - {} - {}'.format(self.fecha, self.cliente, self.moneda_monto)

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

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('fecha',)
        verbose_name = 'orden de compra'
        verbose_name_plural = 'ordenes de compras'
