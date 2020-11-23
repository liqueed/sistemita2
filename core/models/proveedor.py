from django.db import models

from core.models.utils import TimeStampedModel, FacturaAbstract
from core.models.entidad import Provincia, Distrito, Localidad
from core.models.archivo import Archivo
from core.models.cliente import Factura


class Proveedor(TimeStampedModel, models.Model):
    razon_social = models.CharField('Razón Social', blank=False, null=False, max_length=128)
    cuit = models.CharField('CUIT', blank=False, null=False, max_length=11)
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
        ordering = ('razon_social',)
        verbose_name = 'proveedor'
        verbose_name_plural = 'proveedores'

    def __str__(self):
        return f'{self.razon_social} - {self.cuit}'


class FacturaProveedor(FacturaAbstract):
    """Modelo de factura de proveedor."""
    proveedor = models.ForeignKey(Proveedor, blank=False, on_delete=models.CASCADE)
    archivos = models.ManyToManyField(Archivo, blank=True)
    factura = models.ForeignKey(Factura, blank=False, on_delete=models.CASCADE)

    @property
    def moneda_monto(self):
        return f'{self.get_moneda_display()} {self.total}'

    def __str__(self):
        return '{} - {} - {}'.format(self.fecha, self.proveedor, self.moneda_monto)

    class Meta:
        ordering = ('fecha',)
        verbose_name = 'factura proveedor'
        verbose_name_plural = 'facturas proveedores'
