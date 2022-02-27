"""Proveedor factories."""

# Fake
import factory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker as fake

# Sistemita
from sistemita.core.constants import MONEDAS, TIPOS_FACTURA, ZERO_DECIMAL
from sistemita.core.models import (
    Distrito,
    FacturaProveedor,
    FacturaProveedorCategoria,
    Localidad,
    Proveedor,
    Provincia,
)
from sistemita.core.tests.factories import (
    ArchivoFactory,
    FacturaClienteFactory,
)
from sistemita.core.utils.commons import get_porcentaje_agregado
from sistemita.utils.tests import generate_dict_factory, rand_range

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


class FacturaProveedorFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de facturas de proveedor."""

    class Meta:
        """Factory settings."""

        model = FacturaProveedor

    proveedor = SubFactory(ProveedorFactory)
    factura = SubFactory(FacturaClienteFactory)

    fecha = Faker('date_this_month')
    numero = Faker('random_number', digits=10)
    tipo = Faker('random_element', elements=[row[0] for row in TIPOS_FACTURA])
    categoria = SubFactory(FacturaProveedorCategoriaFactory)

    detalle = Faker('text', max_nb_chars=50)
    moneda = Faker('random_element', elements=[row[0] for row in MONEDAS])
    neto = Faker('pydecimal', max_value=10000, positive=True, right_digits=2)
    iva = Faker('random_number', digits=2)
    total = factory.LazyAttribute(lambda o: get_porcentaje_agregado(amount=o.neto, percentage=o.iva))
    cobrado = Faker('pybool')

    monto_imputado = ZERO_DECIMAL

    @factory.post_generation
    def archivos(self, create, extracted, **kwargs):
        """Asigna archivos a la factory."""
        if not create or not extracted:
            return
        self.archivos.add(*extracted)


class FacturaProveedorFactoryData:
    """Creación de datos para el modelo de factura de proveedor."""

    def __init__(self):
        FacturaProveedorDictFactory = generate_dict_factory(FacturaProveedorFactory)
        proveedor = ProveedorFactory.create()
        categoria = FacturaProveedorCategoriaFactory.create()
        archivo = ArchivoFactory.build()

        # De forma aleatoria se elige o no asociarla a una factura a cliente
        with_factura = rand_range(0, 1)
        factura = FacturaClienteFactory.create().pk if with_factura else None
        self.data = FacturaProveedorDictFactory()
        self.data.update({'proveedor': proveedor.pk})
        self.data.update({'factura': factura})
        self.data.update({'categoria': categoria.pk})
        self.data.update({'archivos': archivo.documento.file})
        self.data.update({'monto_imputado': 0.0})

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data
