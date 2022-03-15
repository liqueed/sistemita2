"""Cobranza factories."""

# Fake
import factory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

# Sistemita
from sistemita.accounting.models import Pago, PagoFactura, PagoFacturaPago
from sistemita.core.constants import MONEDAS
from sistemita.core.tests.factories import (
    FacturaProveedorFactory,
    MedioPagoFactory,
    ProveedorFactory,
)
from sistemita.utils.tests import generate_dict_factory


class PagoFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de pago."""

    class Meta:
        """Factories settings."""

        model = Pago

    proveedor = SubFactory(ProveedorFactory)

    fecha = Faker('date_this_month')
    moneda = Faker('random_element', elements=[row[0] for row in MONEDAS])
    total = Faker('pydecimal', max_value=1, positive=True, right_digits=2)
    pagado = True


class PagoFactoryData:
    """Creación de datos para el modelo de pagos."""

    def __init__(self):
        PagoFactoryDictFactory = generate_dict_factory(PagoFactory)
        self.data = PagoFactoryDictFactory()

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data


class PagoFacturaFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de facturas de pago."""

    class Meta:
        """Factory settings."""

        model = PagoFactura

    pago = SubFactory(PagoFactory)
    factura = SubFactory(FacturaProveedorFactory, proveedor=factory.SelfAttribute('..pago.proveedor'))

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
