"""Fondo factories."""

# Fake
import factory
from factory import SubFactory
from factory.django import DjangoModelFactory

# Sistemita
from sistemita.core.tests.factories import FacturaClienteFactory
from sistemita.core.utils.commons import get_porcentaje
from sistemita.expense.models import Fondo
from sistemita.utils.tests import generate_dict_factory


class FondoFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de fondos."""

    class Meta:
        """Factory settings."""

        model = Fondo

    factura = SubFactory(FacturaClienteFactory)
    moneda = factory.LazyAttribute(lambda o: o.factura.moneda)
    monto = factory.LazyAttribute(lambda o: get_porcentaje(o.factura.total, o.factura.porcentaje_fondo))
    monto_disponible = factory.LazyAttribute(lambda o: get_porcentaje(o.factura.total, o.factura.porcentaje_fondo))
    disponible = True


class FondoFactoryData:
    """ClienteFactoryData model."""

    def __init__(self):

        FondoDictFactory = generate_dict_factory(FondoFactory)
        self.data = FondoDictFactory()

    def build(self):
        """Building data for forms."""
        return self.data
