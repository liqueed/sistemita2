"""Proveedor factories."""

from factory import Faker
from factory.django import DjangoModelFactory
from faker import Faker as fake

# Sistemita
from sistemita.core.models import (
    Distrito,
    FacturaProveedorCategoria,
    Localidad,
    Proveedor,
    Provincia,
)
from sistemita.utils.tests import generate_dict_factory

fake = fake()


class ProveedorFactory(DjangoModelFactory):
    """ProveedorFactory factory."""

    razon_social = Faker('name')
    cuit = Faker('random_number', digits=11, fix_len=True)
    correo = Faker('email')
    telefono = Faker('bothify', text='+##########')
    calle = Faker('name')
    numero = Faker('random_number', digits=4)
    piso = Faker('random_number', digits=2)
    dpto = Faker('bothify', text='?')
    cbu = Faker('random_number', digits=22)

    class Meta:
        """Factory settings."""

        model = Proveedor
        django_get_or_create = ('razon_social', 'correo', 'cuit')


class ProveedorFactoryData:
    """ProverdorFactoryData model."""

    def __init__(self):

        provincia = Provincia.objects.order_by('?').first()
        distrito = Distrito.objects.filter(provincia=provincia).order_by('?').first()
        localidad = Localidad.objects.filter(distrito=distrito).order_by('?').first()

        ProveedorFactoryDictFactory = generate_dict_factory(ProveedorFactory)
        self.data = ProveedorFactoryDictFactory()
        self.data.update({'provincia': provincia.pk})
        self.data.update({'distrito': distrito.pk})
        self.data.update({'localidad': localidad.pk})

    def build(self):
        """Building data for forms."""
        return self.data


class FacturaProveedorCategoriaFactory(DjangoModelFactory):
    """Factory categoría de factura de proveedores que herada de DjangoModelFactory."""

    class Meta:
        """Factory settings."""

        model = FacturaProveedorCategoria
        django_get_or_create = ('nombre',)

    nombre = Faker('random_element', elements=('COACH', 'CONTABILODAD', 'EQUIPO LIQUEED', 'OTROS GASTOS'))


class FacturaProveedorCategoriaFactoryData:
    """Creación de datos para el modelo de categoría de facturas a proveedores."""

    def __init__(self):
        FacturaProveedorCategoriaDictFactory = generate_dict_factory(FacturaProveedorCategoriaFactory)
        self.data = FacturaProveedorCategoriaDictFactory()

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data
