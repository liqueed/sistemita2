from decimal import Decimal

# Fake
import factory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker as fake

# Sistemita
from sistemita.core.constants import MONEDAS, TIPOS_FACTURA, ZERO_DECIMAL
from sistemita.core.models import (
    Distrito,
    FacturaDistribuidaProveedor,
    FacturaProveedor,
    FacturaProveedorCategoria,
    FacturaProveedorImputada,
    Localidad,
    Proveedor,
    Provincia,
)
from sistemita.core.tests.factories import (
    ArchivoFactory,
    FacturaClienteFactory,
    FacturaDistribuidaFactory,
)
from sistemita.utils.commons import get_porcentaje_agregado, get_total_factura
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

        # De forma aleatoria se elige o no asociarla a una factura a proveedor
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


class FacturaImputadaProveedorFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de facturas imputadas de proveedores."""

    class Meta:
        """Factory settings."""

        model = FacturaProveedorImputada

    proveedor = SubFactory(ProveedorFactory)
    nota_de_credito = SubFactory(FacturaProveedorFactory)

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
        self.nota_de_credito.proveedor = self.proveedor

        self.monto_facturas = 0
        self.total_factura = 0

        total_nc = self.nota_de_credito.total
        for factura in self.facturas.all():
            self.monto_facturas += Decimal(factura.total)
            factura.moneda = self.moneda
            factura.proveedor = self.proveedor
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


class FacturaImputadaProveedorFactoryData:
    """Creación de datos para el modelo de factura imputada de proveedores."""

    def __init__(self):
        proveedor = ProveedorFactory.create()
        nota_de_credito = FacturaProveedorFactory.create(
            proveedor=proveedor,
            tipo='NC',
            cobrado=False,
        )

        facturas = []
        facturas_id = []
        monto_facturas = 0
        for _ in range(0, rand_range(2, 5)):
            factura = FacturaProveedorFactory.create(
                proveedor=proveedor, moneda=nota_de_credito.moneda, tipo='A', cobrado=False
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
            'proveedor_id': proveedor.pk,
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
            'proveedor_id': instance.proveedor.pk,
            'nota_de_credito_id': instance.nota_de_credito.pk,
            'moneda': instance.moneda,
            'monto_facturas': monto_facturas,
            'monto_nota_de_credito': instance.monto_nota_de_credito,
            'total_factura': total_factura,
            'facturas_list': facturas_list,
        }


class FacturaDistribuidaProveedorFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de facturas distribuidas a proveedor."""

    class Meta:
        """Factory settings."""

        model = FacturaDistribuidaProveedor

    factura_distribucion = SubFactory(FacturaDistribuidaFactory)
    proveedor = SubFactory(ProveedorFactory)
    detalle = Faker('text', max_nb_chars=255)
