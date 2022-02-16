"""Cliente factories."""

# Django
from django.utils import timezone

# Fake
from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

# Sistemita
from sistemita.core.constants import MONEDAS
from sistemita.core.models import (
    Cliente,
    Distrito,
    FacturaCategoria,
    Localidad,
    OrdenCompra,
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


class OrdenCompraFactoryData:
    """Creación de datos para el modelo de orden de compra de clientes."""

    def __init__(self):
        self.data = {
            'fecha': timezone.datetime.strptime(fake.date(), '%Y-%m-%d').strftime('%d/%m/%Y'),
            'cliente': ClienteFactory.create().pk,
            'moneda': rand_element_from_array(MONEDAS)[0],
            'monto': str(fake.pydecimal(2, 2, True)),
        }

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data


class OrdenCompraFactory(DjangoModelFactory):
    """Fabrica de datos del modelo orden compra de clientes."""

    class Meta:
        """Factory settings."""

        model = OrdenCompra

    fecha = fake.date()
    cliente = SubFactory(ClienteFactory)
    moneda = rand_element_from_array(MONEDAS)[0]
    monto = str(fake.pydecimal(2, 2, True))
