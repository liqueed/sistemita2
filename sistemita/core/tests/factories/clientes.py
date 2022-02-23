"""Cliente factories."""

from decimal import Decimal

# Fake
import factory
from django.utils import timezone
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker as fake

# Sistemita
from sistemita.core.constants import MONEDAS, TIPOS_FACTURA, ZERO_DECIMAL
from sistemita.core.models import (
    Cliente,
    Distrito,
    Factura,
    FacturaCategoria,
    FacturaImputada,
    Localidad,
    OrdenCompra,
    Provincia,
)
from sistemita.core.tests.factories import ArchivoFactory
from sistemita.core.utils.commons import get_porcentaje_agregado
from sistemita.utils.tests import generate_dict_factory, rand_range

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
    monto_imputado = ZERO_DECIMAL

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


class FacturaImputadaClienteFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de facturas imputadas de clientes."""

    class Meta:
        """Factory settings."""

        model = FacturaImputada

    cliente = SubFactory(ClienteFactory)
    nota_de_credito = SubFactory(FacturaClienteFactory)

    fecha = Faker('date_this_month')
    moneda = Faker('random_element', elements=[row[0] for row in MONEDAS])
    monto_facturas = Faker('pydecimal', max_value=1, positive=True, right_digits=2)
    monto_nota_de_credito = factory.LazyAttribute(lambda o: o.nota_de_credito.total)
    total_factura = Faker('pydecimal', max_value=1, positive=True, right_digits=2)

    @factory.post_generation
    def facturas(self, create, extracted, **kwargs):
        """Asigna facturas a la factory."""
        if not create or not extracted:
            return
        self.facturas.add(*extracted)

        self.nota_de_credito.tipo = 'NC'
        self.nota_de_credito.moneda = self.moneda
        self.nota_de_credito.cliente = self.cliente

        self.monto_facturas = 0
        self.total_factura = 0

        for factura in self.facturas.all():
            self.monto_facturas += Decimal(factura.total)
            factura.moneda = self.moneda
            factura.cliente = self.cliente
            if self.nota_de_credito.total > 0:
                amount = self.nota_de_credito.total - factura.total
                self.nota_de_credito.total = max(amount, ZERO_DECIMAL)
                factura.total -= abs(amount)
                factura.monto_imputado = abs(amount)
            factura.save()

        self.nota_de_credito.save()
        self.total_factura = max(self.monto_facturas - self.monto_nota_de_credito, ZERO_DECIMAL)


class FacturaImputadaClienteFactoryData:
    """Creación de datos para el modelo de factura imputada de clientes."""

    def __init__(self):
        cliente = ClienteFactory.create()
        nota_de_credito = FacturaClienteFactory.create(
            cliente=cliente,
            tipo='NC',
            cobrado=False,
        )

        facturas = []
        facturas_id = []
        monto_facturas = 0
        for _ in range(0, rand_range(2, 5)):
            factura = FacturaClienteFactory.create(
                cliente=cliente, moneda=nota_de_credito.moneda, tipo='A', cobrado=False
            )
            facturas_id.append(factura.pk)
            facturas.append(factura)
            monto_facturas += factura.total
            if nota_de_credito.total != 0:
                nota_de_credito.total -= factura.total
                nota_de_credito.monto_imputado += factura.total

        total_factura = max(monto_facturas - nota_de_credito.total, ZERO_DECIMAL)
        nota_de_credito.save()
        facturas_list = []
        for pk in facturas_id:
            facturas_list.append({'factura': pk, 'action': 'add'})

        self.data_create = {
            'cliente_id': cliente.pk,
            'nota_de_credito_id': nota_de_credito.pk,
            'fecha': nota_de_credito.fecha,
            'moneda': nota_de_credito.moneda,
            'monto_facturas': monto_facturas,
            'monto_nota_de_credito': nota_de_credito.total,
            'total_factura': total_factura,
            'facturas_list': facturas_list,
        }

    def create(self):
        """Devuelve un diccionario con datos."""
        return self.data_create

    @staticmethod
    def update(instance, facturas_list, monto_facturas, total_factura):
        """Devuelve un diccionario con datos para editar."""
        return {
            'fecha': instance.fecha,
            'cliente_id': instance.cliente.pk,
            'nota_de_credito_id': instance.nota_de_credito.pk,
            'moneda': instance.moneda,
            'monto_facturas': monto_facturas,
            'monto_nota_de_credito': instance.monto_nota_de_credito,
            'total_factura': total_factura,
            'facturas_list': facturas_list,
        }
