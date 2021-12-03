"""Modelo de proveedor y sus relaciones."""

# Django
from django.db import models

# Utils
from sistemita.core.constants import MONEDAS

# Models
from sistemita.core.models.archivo import Archivo
from sistemita.core.models.cliente import Factura
from sistemita.core.models.entidad import Distrito, Localidad, Provincia
from sistemita.core.models.utils import FacturaAbstract, TimeStampedModel


class Proveedor(TimeStampedModel, models.Model):
    """Modelo proveedor."""

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

    cbu = models.CharField(max_length=22, blank=True, verbose_name='CBU')

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('razon_social',)
        verbose_name = 'proveedor'
        verbose_name_plural = 'proveedores'

    def __str__(self):
        """Devuelve una representación legible del modelo."""
        return f'{self.razon_social} - {self.cuit}'

    @property
    def calle_numero(self):
        "Retorna la direccion completa."
        return '{} Nro: {} '.format(self.calle, self.numero)


class FacturaProveedor(FacturaAbstract):
    """Modelo de factura de proveedor."""

    proveedor = models.ForeignKey(Proveedor, blank=False, on_delete=models.CASCADE)
    archivos = models.ManyToManyField(Archivo, blank=True)
    factura = models.ForeignKey(
        Factura, blank=True, null=True, on_delete=models.CASCADE, related_name='facturas_proveedor'
    )

    @property
    def moneda_monto(self):
        """Retorna el total con su moneda."""
        return f'{self.get_moneda_display()} {self.total}'

    def __str__(self):
        """Retorna una representación legible del modelo."""
        return '{} - {} - {}'.format(self.fecha, self.proveedor, self.moneda_monto)

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('fecha',)
        verbose_name = 'factura proveedor'
        verbose_name_plural = 'facturas proveedores'


class FacturaProveedorImputada(TimeStampedModel, models.Model):
    """Modelo de imputación de facturas de proveedores."""

    fecha = models.DateField(blank=False)
    proveedor = models.ForeignKey(Proveedor, blank=False, on_delete=models.CASCADE)
    facturas = models.ManyToManyField(FacturaProveedor, related_name='facturas_imputacion')
    nota_de_credito = models.OneToOneField(
        FacturaProveedor, blank=True, null=True, on_delete=models.SET_NULL, related_name='factura_nc'
    )
    moneda = models.CharField(blank=False, max_length=1, choices=MONEDAS, default='P')
    monto_facturas = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    monto_nota_de_credito = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)
    total_factura = models.DecimalField(blank=False, decimal_places=2, max_digits=12, default=0.0)

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('fecha',)
        verbose_name = 'factura proveedor imputada'
        verbose_name_plural = 'facturas proveedor imputadas'
