"""Proveedor factories."""

from factory.django import DjangoModelFactory
from faker import Faker

# Sistemita
from sistemita.core.models import (
    Distrito,
    FacturaProveedorCategoria,
    Localidad,
    Proveedor,
    Provincia,
)
from sistemita.utils.tests import rand_element_from_array, randN

fake = Faker('es_ES')


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


class FacturaProveedorCategoriaFactoryData:
    """Creación de datos para el modelo de categoría de facturas a proveedores."""

    _categorias = [
        'COACH',
        'CONTABILODAD',
        'EQUIPO LIQUEED',
        'OTROS GASTOS',
    ]

    def __init__(self):
        self.nombre = rand_element_from_array(self._categorias)
        self.data = {'nombre': self.nombre}

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data


class FacturaProveedorCategoriaFactory(DjangoModelFactory):
    """Factory categoría de factura de proveedores que herada de DjangoModelFactory."""

    class Meta:
        """Factory settings."""

        model = FacturaProveedorCategoria
        django_get_or_create = ('nombre',)

    nombre = FacturaProveedorCategoriaFactoryData().nombre
