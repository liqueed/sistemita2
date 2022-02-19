"""Cliente factories."""

# Fake
import factory
from django.utils import timezone
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker as fake

# Sistemita
from sistemita.core.constants import MONEDAS, TIPOS_FACTURA
from sistemita.core.models import (
    Cliente,
    Distrito,
    Factura,
    FacturaCategoria,
    Localidad,
    OrdenCompra,
    Provincia,
)
from sistemita.core.tests.factories import ArchivoFactory
from sistemita.core.utils.commons import get_porcentaje_agregado
from sistemita.utils.tests import generate_dict_factory

fake = fake()


class ClienteFactory(DjangoModelFactory):
    """Fabrica de datos de cliente."""

    razon_social = Faker('name')
    cuit = Faker('random_number', digits=11, fix_len=True)
    correo = Faker('email')
    telefono = Faker('bothify', text='+##########')
    calle = Faker('name')
    numero = Faker('random_number', digits=4)
    piso = Faker('random_number', digits=2)
    dpto = Faker('bothify', text='?')

    class Meta:
        """Factory settings."""

        model = Cliente
        django_get_or_create = ('razon_social', 'correo', 'cuit')


class ClienteFactoryData:
    """ClienteFactoryData model."""

    def __init__(self):

        provincia = Provincia.objects.order_by('?').first()
        distrito = Distrito.objects.filter(provincia=provincia).order_by('?').first()
        localidad = Localidad.objects.filter(distrito=distrito).order_by('?').first()

        ClienteDictFactory = generate_dict_factory(ClienteFactory)
        self.data = ClienteDictFactory()
        self.data.update({'provincia': provincia.pk})
        self.data.update({'distrito': distrito.pk})
        self.data.update({'localidad': localidad.pk})

    def build(self):
        """Building data for forms."""
        return self.data


class FacturaClienteCategoriaFactory(DjangoModelFactory):
    """Factory categoría de factura a cliente que herada de DjangoModelFactory."""

    class Meta:
        """Factory settings."""

        model = FacturaCategoria
        django_get_or_create = ('nombre',)

    nombre = Faker('random_element', elements=('ACOMPAÑAMIENTO', 'CURSO CSM', 'CURSO CSPO', 'WORKSHOP'))


class FacturaClienteCategoriaFactoryData:
    """Creación de datos para el modelo de categoría de facturas a clientes."""

    def __init__(self):
        FacturaClienteCategoriaDictFactory = generate_dict_factory(FacturaClienteCategoriaFactory)
        self.data = FacturaClienteCategoriaDictFactory()

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data


class OrdenCompraFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo orden compra de clientes."""

    class Meta:
        """Factory settings."""

        model = OrdenCompra

    cliente = SubFactory(ClienteFactory)
    fecha = Faker('date_this_month')
    moneda = Faker('random_element', elements=[row[0] for row in MONEDAS])
    monto = Faker('pydecimal', max_value=10000000, positive=True)


class OrdenCompraFactoryData:
    """Creación de datos para el modelo de orden de compra de clientes."""

    def __init__(self):
        OrdenCompraDictFactory = generate_dict_factory(OrdenCompraFactory)
        self.data = OrdenCompraDictFactory()
        self.data.update({'fecha': timezone.datetime.strptime(fake.date(), '%Y-%m-%d').strftime('%d/%m/%Y')})
        self.data.update({'cliente': ClienteFactory.create().pk})
        self.data.update({'monto': str(fake.pydecimal(2, 2, True))})

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data


class FacturaClienteFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de facturas de clientes."""

    class Meta:
        """Factory settings."""

        model = Factura

    fecha = Faker('date_this_month')
    numero = Faker('random_number', digits=10)
    tipo = Faker('random_element', elements=[row[0] for row in TIPOS_FACTURA])
    categoria = SubFactory(FacturaClienteCategoriaFactory)

    cliente = SubFactory(ClienteFactory)

    detalle = Faker('text', max_nb_chars=50)
    moneda = Faker('random_element', elements=[row[0] for row in MONEDAS])
    neto = Faker('pydecimal', max_value=10000, positive=True, right_digits=2)
    iva = Faker('random_number', digits=2)
    total = factory.LazyAttribute(lambda o: get_porcentaje_agregado(amount=o.neto, percentage=o.iva))
    cobrado = Faker('pybool')

    porcentaje_fondo = Faker('random_number', digits=2)
    monto_imputado = factory.LazyAttribute(
        lambda o: get_porcentaje_agregado(amount=o.total, percentage=o.porcentaje_fondo)
    )

    @factory.post_generation
    def archivos(self, create, extracted, **kwargs):
        """Asigna archivos a la factory."""
        if not create or not extracted:
            return
        self.archivos.add(*extracted)


class FacturaClienteFactoryData:
    """Creación de datos para el modelo de factura de clientes."""

    def __init__(self):
        FacturaClienteDictFactory = generate_dict_factory(FacturaClienteFactory)
        cliente = ClienteFactory.create()
        categoria = FacturaClienteCategoriaFactory.create()
        archivo = ArchivoFactory.build()
        self.data = FacturaClienteDictFactory()
        self.data.update({'cliente': cliente.pk})
        self.data.update({'categoria': categoria.pk})
        self.data.update({'archivos': archivo.documento.file})
        self.data.update({'monto_imputado': 0.0})

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data
