"""Modelo de cliente."""

# Django
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Utils
from sistemita.core.constants import MONEDAS

# Models
from sistemita.core.models.archivo import Archivo
from sistemita.core.models.entidad import Distrito, Localidad, Provincia
from sistemita.core.models.utils import FacturaAbstract, TimeStampedModel
from sistemita.expense.models import Fondo


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


class Factura(FacturaAbstract):
    """Modelo factura de cliente."""

    cliente = models.ForeignKey(Cliente, blank=False, on_delete=models.CASCADE)
    archivos = models.ManyToManyField(Archivo, blank=True)
    porcentaje_fondo = models.PositiveSmallIntegerField(default=15)

    def __str__(self):
        """Devuelve una represetación legible del modelo."""
        return '{} -{} - {} - {}'.format(self.fecha, self.numero, self.cliente.razon_social, self.moneda_monto)

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

    class Meta:
        """Configuraciones del modelo."""

        ordering = ('fecha',)
        verbose_name = 'orden de compra'
        verbose_name_plural = 'ordenes de compras'


@receiver(post_save, sender=Factura)
def post_save_factura(sender, instance, created, **kwargs):
    """Crea una instancia de fondo asociada a una factura si no existe."""
    if not Fondo.objects.filter(factura=instance).exists():
        Fondo.objects.create(factura=instance, monto=instance.porcentaje_fondo_monto)
