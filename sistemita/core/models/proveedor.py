"""Modelo de proveedor y sus relaciones."""

# Django
from django.db import models

# Models
from sistemita.core.models.archivo import Archivo
from sistemita.core.models.cliente import Factura
from sistemita.core.models.entidad import Distrito, Localidad, Provincia
from sistemita.core.models.utils import FacturaAbstract, TimeStampedModel


class Proveedor(TimeStampedModel, models.Model):
    """Modelo proveedor."""

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

    cbu = models.CharField(max_length=22, blank=True, null=True, verbose_name='CBU')

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
    factura = models.ForeignKey(Factura, blank=False, on_delete=models.CASCADE)

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
