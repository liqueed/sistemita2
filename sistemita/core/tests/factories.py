"""Core factories."""

from factory.django import DjangoModelFactory
from faker import Faker

# Sistemita
from sistemita.core.models import (
    Cliente,
    Distrito,
    FacturaCategoria,
    Localidad,
    MedioPago,
    Proveedor,
    Provincia,
)
from sistemita.utils.tests import rand_element_from_array, randN

fake = Faker('es_ES')


class ClienteFactory(DjangoModelFactory):
    """Fabrica de datos de cliente."""

    razon_social = fake.name()
    cuit = randN(11)
    correo = fake.email()
    telefono = fake.phone_number()[0:14]
    calle = fake.name()[0:35]
    numero = fake.numerify(text='##@@')
    piso = fake.numerify(text='#@')
    dpto = fake.lexify(text='?')

    class Meta:
        """Factory settings."""

        model = Cliente
        django_get_or_create = ('razon_social',)


class ClienteFactoryData:
    """ClienteFactoryData model."""

    def __init__(self):

        provincia = Provincia.objects.order_by('?').first()
        distrito = Distrito.objects.filter(provincia=provincia).order_by('?').first()
        localidad = Localidad.objects.filter(distrito=distrito).order_by('?').first()

        self.data = {
            'razon_social': fake.name(),
            'cuit': randN(11),
            'correo': fake.email(),
            'telefono': fake.phone_number()[0:14],
            'calle': fake.name()[0:35],
            'numero': fake.numerify(text='##@@'),
            'piso': fake.numerify(text='#@'),
            'dpto': fake.lexify(text='?'),
            'provincia': provincia.pk,
            'distrito': distrito.pk,
            'localidad': localidad.pk,
        }

    def build(self):
        """Building data for forms."""
        return self.data


class ProveedorFactory(DjangoModelFactory):
    """ProveedorFactory factory."""

    razon_social = fake.name()
    cuit = randN(11)
    correo = fake.email()
    telefono = fake.phone_number()[0:14]
    calle = fake.name()[0:35]
    numero = fake.numerify(text='##@@')
    piso = fake.numerify(text='#@')
    dpto = fake.lexify(text='?')
    cbu = randN(11)

    class Meta:
        """Factory settings."""

        model = Proveedor
        django_get_or_create = ('razon_social',)


class ProveedorFactoryData:
    """ProverdorFactoryData model."""

    def __init__(self):

        provincia = Provincia.objects.order_by('?').first()
        distrito = Distrito.objects.filter(provincia=provincia).order_by('?').first()
        localidad = Localidad.objects.filter(distrito=distrito).order_by('?').first()

        self.data = {
            'razon_social': fake.name(),
            'cuit': randN(11),
            'correo': fake.email(),
            'telefono': fake.phone_number()[0:14],
            'calle': fake.name()[0:35],
            'numero': fake.numerify(text='##@@'),
            'piso': fake.numerify(text='#@'),
            'dpto': fake.lexify(text='?'),
            'provincia': provincia.pk,
            'distrito': distrito.pk,
            'localidad': localidad.pk,
            'cbu': randN(11),
        }

    def build(self):
        """Building data for forms."""
        return self.data


class MedioPagoFactoryData:
    """Creación de datos para el modelo de Medio de pagos."""

    _medios = [
        'Cheque',
        'Efectivo',
        'Imputación interna',
        'Mercado pago',
        'Paypal',
        'Tarjeta de crédito',
        'Transferencia',
    ]

    def __init__(self):
        self.nombre = rand_element_from_array(self._medios)
        self.data = {'nombre': self.nombre}

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data


class MedioPagoFactory(DjangoModelFactory):
    """Medio de pago factory que herada de DjangoModelFactory."""

    class Meta:
        """Factory settings."""

        model = MedioPago
        django_get_or_create = ('nombre',)

    nombre = MedioPagoFactoryData().nombre


class FacturaClienteCategoriaFactoryData:
    """Creación de datos para el modelo de categoría de facturas a clientes."""

    _categorias = [
        'ACOMPAÑAMIENTO',
        'CURSO CSM',
        'CURSO CSPO',
        'WORKSHOP',
    ]

    def __init__(self):
        self.nombre = rand_element_from_array(self._categorias)
        self.data = {'nombre': self.nombre}

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data


class FacturaClienteCategoriaFactory(DjangoModelFactory):
    """Factory categoría de factura a cliente que herada de DjangoModelFactory."""

    class Meta:
        """Factory settings."""

        model = FacturaCategoria
        django_get_or_create = ('nombre',)

    nombre = FacturaClienteCategoriaFactoryData().nombre
