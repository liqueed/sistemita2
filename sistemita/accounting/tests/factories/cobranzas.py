"""Cobranza factories."""

# Fake
import factory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker as Fake

# Sistemita
from sistemita.accounting.models import (
    Cobranza,
    CobranzaFactura,
    CobranzaFacturaPago,
)
from sistemita.core.constants import MONEDAS
from sistemita.core.models import MedioPago
from sistemita.core.tests.factories import (
    ClienteFactory,
    FacturaClienteFactory,
    MedioPagoFactory,
)
from sistemita.utils.tests import (
    generate_dict_factory,
    rand_element_from_array,
    rand_range,
)

fake = Fake()


class CobranzaFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de cobranza."""

    class Meta:
        """Factories settings."""

        model = Cobranza

    cliente = SubFactory(ClienteFactory)

    fecha = Faker('date_this_month')
    moneda = Faker('random_element', elements=[row[0] for row in MONEDAS])
    total = Faker('pydecimal', max_value=1, positive=True, right_digits=2)


class CobranzaFactoryData:
    """Creación de datos para el modelo de cobranzas."""

    def __init__(self):
        self.instance = CobranzaFactory
        CobranzaFactoryDictFactory = generate_dict_factory(self.instance)
        self.data = CobranzaFactoryDictFactory()

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data

    def create(self):
        """Genera datos para el endpoint de crear."""
        cobranza_facturas = []
        total = 0
        cliente = ClienteFactory.create()
        moneda = rand_element_from_array([row[0] for row in MONEDAS])
        for _ in range(0, 2):
            factura = FacturaClienteFactory.create(cliente=cliente, cobrado=False, moneda=moneda, tipo='A')
            total += factura.total
            cobranza_facturas.append(
                {
                    'factura': factura.pk,
                    'ganancias': 0,
                    'ingresos_brutos': 0,
                    'iva': 0,
                    'suss': 0,
                    'cobranza_factura_pagos': [
                        {'metodo': MedioPago.objects.order_by('?').first().pk, 'monto': fake.pydecimal(2, 2, True)}
                    ],
                }
            )

        data = {
            'fecha': fake.date_this_month(),
            'cliente': {
                'razon_social': cliente.razon_social,
                'cuit': str(cliente.cuit),
                'correo': cliente.correo,
                'telefono': cliente.telefono,
            },
            'moneda': moneda,
            'total': total,
            'cobranza_facturas': cobranza_facturas,
        }
        return data

    def update(self):
        """Construye un diccionario con una cobranza existente."""
        cobranza = self.instance.create()
        limit = rand_range(1, 3)
        for _ in range(0, limit):
            cobranza_factura = CobranzaFacturaFactory.create(cobranza=cobranza)
            CobranzaFacturaPagoFactory.create(cobranza_factura=cobranza_factura)
            cobranza.total += cobranza_factura.factura.total

        cobranza.save()
        cobranza_facturas = []
        for item in cobranza.cobranza_facturas.all():
            cobranza_facturas.append(
                {
                    'factura': item.factura.pk,
                    'data': {'id': item.pk, 'action': 'update'},
                    'ganancias': item.ganancias,
                    'ingresos_brutos': item.ingresos_brutos,
                    'iva': item.iva,
                    'suss': item.suss,
                    'cobranza_factura_pagos': [
                        {
                            'data': {'id': item.cobranza_factura_pagos.all().first().pk, 'action': 'update'},
                            'metodo': item.cobranza_factura_pagos.first().metodo.pk,
                            'monto': item.cobranza_factura_pagos.first().monto,
                        }
                    ],
                }
            )

        data = {
            'id': cobranza.id,
            'fecha': cobranza.fecha,
            'cliente': {
                'razon_social': cobranza.cliente.razon_social,
                'cuit': str(cobranza.cliente.cuit),
                'correo': cobranza.cliente.correo,
                'telefono': cobranza.cliente.telefono,
            },
            'moneda': cobranza.moneda,
            'total': cobranza.total,
            'cobranza_facturas': cobranza_facturas,
        }

        return data


class CobranzaFacturaFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de facturas de cobranza."""

    class Meta:
        """Factory settings."""

        model = CobranzaFactura

    cobranza = SubFactory(CobranzaFactory)
    factura = SubFactory(
        FacturaClienteFactory,
        cliente=factory.SelfAttribute('..cobranza.cliente'),
        moneda=factory.SelfAttribute('..cobranza.moneda'),
    )

    ganancias = Faker('pydecimal', max_value=1, positive=True, right_digits=2)
    ingresos_brutos = Faker('pydecimal', max_value=1, positive=True, right_digits=2)
    iva = Faker('pydecimal', max_value=1, positive=True, right_digits=2)
    suss = Faker('pydecimal', max_value=1, positive=True, right_digits=2)


class CobranzaFacturaFactoryData:
    """Creación de datos para el modelo de facturas de cobranzas."""

    def __init__(self):
        CobranzaFacturaDictFactory = generate_dict_factory(CobranzaFacturaFactory)
        self.data = CobranzaFacturaDictFactory()

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data


class CobranzaFacturaPagoFactory(DjangoModelFactory):
    """Fabrica de instancia del modelo pagos de facturas de cobranzas."""

    class Meta:
        """Factory settings."""

        model = CobranzaFacturaPago

    cobranza_factura = SubFactory(CobranzaFacturaFactory)
    metodo = SubFactory(MedioPagoFactory)
    monto = Faker('pydecimal', max_value=1, positive=True, right_digits=2)


class CobranzaFacturaPagoFactoryData:
    """Creación de datos para el modelo de pagos de facturas de cobranzas."""

    def __init__(self):
        CobranzaFacturaPagoDictFactory = generate_dict_factory(CobranzaFacturaPagoFactory)
        self.data = CobranzaFacturaPagoDictFactory()

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data
