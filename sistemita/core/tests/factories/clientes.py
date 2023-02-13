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
    FacturaDistribuida,
    FacturaImputada,
    Localidad,
    OrdenCompra,
    Provincia,
)
from sistemita.core.tests.factories import ArchivoFactory
from sistemita.utils.commons import get_porcentaje_agregado, get_total_factura
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
    porcentaje_socio_alan = Faker('pydecimal', max_value=20, positive=True, right_digits=2)
    porcentaje_socio_ariel = Faker('pydecimal', max_value=20, positive=True, right_digits=2)

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

        total_nc = self.nota_de_credito.total
        for factura in self.facturas.all():
            self.monto_facturas += Decimal(factura.total)
            factura.moneda = self.moneda
            factura.cliente = self.cliente
            if total_nc > 0:
                factura_total = get_total_factura(factura.total, total_nc)
                factura.monto_imputado = factura.total if factura_total == 0 else total_nc
                total_nc -= factura.total if total_nc > factura.total else total_nc
                factura.total = factura_total
            factura.save()

        self.nota_de_credito.monto_imputado = self.nota_de_credito.total - total_nc
        self.nota_de_credito.total = total_nc
        self.nota_de_credito.cobrado = not bool(self.nota_de_credito.total)
        self.nota_de_credito.save()
        self.total_factura = get_total_factura(self.monto_facturas, self.monto_nota_de_credito)


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

        total_factura = get_total_factura(monto_facturas, nota_de_credito.total_sin_imputar)
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


class FacturaDistribuidaFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de facturas distribuidas de clientes."""

    class Meta:
        """Factory settings."""

        model = FacturaDistribuida

    factura = SubFactory(FacturaClienteFactory)
    distribuida = False
    monto_distribuido = factory.LazyAttribute(lambda o: o.factura.total)


class FacturaDistribuidaFactoryData:
    """Creación de datos para el modelo de factura distribuida a proveedores."""

    def __init__(self):
        from sistemita.core.tests.factories import (  # noqa
            FacturaDistribuidaProveedorFactory,
        )

        factura_distribuida = FacturaDistribuidaFactory.create()
        # factura_distribuida.cobrado = True
        factura_distribuida.save()

        distribucion_list = []
        range_aux = rand_range(2, 5)
        monto = factura_distribuida.factura.monto_neto_sin_fondo_porcentaje_socios / range_aux

        for _ in range(0, range_aux):
            factura_distribuida_proveedor = FacturaDistribuidaProveedorFactory.create()
            distribucion_list.append(
                {
                    'id': factura_distribuida_proveedor.proveedor.pk,
                    'detalle': factura_distribuida_proveedor.detalle,
                    'monto': monto,
                    'data': {'action': 'add'},
                }
            )

        self.data_create = {'factura_distribuida_id': factura_distribuida.pk, 'distribucion_list': distribucion_list}

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data_create

    def create(self):
        """Devuelve un diccionario con datos."""
        return self.data_create

    @staticmethod
    def update(instance):
        """Devuelve un diccionario con datos para editar"""
        distribucion_list = []
        for factura_distribuida_proveedor in instance.factura_distribuida_proveedores.all():
            distribucion_list.append(
                {
                    'proveedor': factura_distribuida_proveedor.proveedor,
                    'detalle': factura_distribuida_proveedor.detalle,
                    'monto': factura_distribuida_proveedor.monto,
                }
            )

        return {'factura_distribuida_id': instance.pk, 'distribucion_list': distribucion_list}
