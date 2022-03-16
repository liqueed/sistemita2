"""Pago factories."""

# Fake
import factory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker as Fake

# Sistemita
from sistemita.accounting.models import Pago, PagoFactura, PagoFacturaPago
from sistemita.core.constants import MONEDAS
from sistemita.core.models import MedioPago
from sistemita.core.tests.factories import (
    FacturaProveedorFactory,
    MedioPagoFactory,
    ProveedorFactory,
)
from sistemita.utils.tests import (
    generate_dict_factory,
    rand_element_from_array,
    rand_range,
)

fake = Fake()


class PagoFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de pago."""

    class Meta:
        """Factories settings."""

        model = Pago

    proveedor = SubFactory(ProveedorFactory)

    fecha = Faker('date_this_month')
    moneda = Faker('random_element', elements=[row[0] for row in MONEDAS])
    total = Faker('pydecimal', max_value=1, positive=True, right_digits=2)
    pagado = Faker('pybool')


class PagoFactoryData:
    """Creación de datos para el modelo de pagos."""

    def __init__(self):
        self.instance = PagoFactory
        PagoFactoryDictFactory = generate_dict_factory(self.instance)
        self.data = PagoFactoryDictFactory()

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data

    def create(self):
        """Genera datos para el endpoint de crear."""
        pago_facturas = []
        total = 0
        proveedor = ProveedorFactory.create()
        moneda = rand_element_from_array([row[0] for row in MONEDAS])
        for _ in range(0, 2):
            factura = FacturaProveedorFactory.create(proveedor=proveedor, cobrado=False, moneda=moneda, tipo='A')
            total += factura.total
            pago_facturas.append(
                {
                    'factura': factura.pk,
                    'ganancias': 0,
                    'ingresos_brutos': 0,
                    'iva': 0,
                    'suss': 0,
                    'pago_factura_pagos': [
                        {'metodo': MedioPago.objects.order_by('?').first().pk, 'monto': fake.pydecimal(2, 2, True)}
                    ],
                }
            )

        data = {
            'fecha': fake.date_this_month(),
            'proveedor': str(proveedor.cuit),
            'moneda': moneda,
            'total': total,
            'pago_facturas': pago_facturas,
            'pagado': fake.pybool(),
        }
        return data

    def update(self):
        """Construye un diccionario con un existente."""
        pago = self.instance.create()
        limit = rand_range(1, 3)
        for _ in range(0, limit):
            pago_factura = PagoFacturaFactory.create(pago=pago)
            PagoFacturaPagoFactory.create(pago_factura=pago_factura)
            pago.total += pago_factura.factura.total

        pago.save()
        pago_facturas = []
        for item in pago.pago_facturas.all():
            pago_facturas.append(
                {
                    'factura': item.factura.pk,
                    'data': {'id': item.pk, 'action': 'update'},
                    'ganancias': item.ganancias,
                    'ingresos_brutos': item.ingresos_brutos,
                    'iva': item.iva,
                    'suss': item.suss,
                    'pago_factura_pagos': [
                        {
                            'data': {'id': item.pago_factura_pagos.all().first().pk, 'action': 'update'},
                            'metodo': item.pago_factura_pagos.first().metodo.pk,
                            'monto': item.pago_factura_pagos.first().monto,
                        }
                    ],
                }
            )

        data = {
            'id': pago.id,
            'fecha': pago.fecha,
            'proveedor': str(pago.proveedor.cuit),
            'moneda': pago.moneda,
            'total': pago.total,
            'pago_facturas': pago_facturas,
        }

        return data


class PagoFacturaFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de facturas de pago."""

    class Meta:
        """Factory settings."""

        model = PagoFactura

    pago = SubFactory(PagoFactory)
    factura = SubFactory(
        FacturaProveedorFactory,
        proveedor=factory.SelfAttribute('..pago.proveedor'),
        moneda=factory.SelfAttribute('..pago.moneda'),
    )

    ganancias = Faker('pydecimal', max_value=1, positive=True, right_digits=2)
    ingresos_brutos = Faker('pydecimal', max_value=1, positive=True, right_digits=2)
    iva = Faker('pydecimal', max_value=1, positive=True, right_digits=2)
    suss = Faker('pydecimal', max_value=1, positive=True, right_digits=2)


class PagoFacturaFactoryData:
    """Creación de datos para el modelo de facturas de pagos."""

    def __init__(self):
        PagoFacturaDictFactory = generate_dict_factory(PagoFacturaFactory)
        self.data = PagoFacturaDictFactory()

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data


class PagoFacturaPagoFactory(DjangoModelFactory):
    """Fabrica de instancia del modelo pagos de facturas de pagos."""

    class Meta:
        """Factory settings."""

        model = PagoFacturaPago

    pago_factura = SubFactory(PagoFacturaFactory)
    metodo = SubFactory(MedioPagoFactory)
    monto = Faker('pydecimal', max_value=1, positive=True, right_digits=2)


class PagoFacturaPagoFactoryData:
    """Creación de datos para el modelo de pagos de facturas de pagos."""

    def __init__(self):
        PagoFacturaPagoDictFactory = generate_dict_factory(PagoFacturaPagoFactory)
        self.data = PagoFacturaPagoDictFactory()

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data
