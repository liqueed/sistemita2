"""Fondo factories."""

# Fake
import factory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

# Sistemita
from sistemita.core.constants import MONEDAS
from sistemita.core.tests.factories import FacturaClienteFactory
from sistemita.expense.models import Fondo
from sistemita.utils.tests import generate_dict_factory


class FondoFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de fondos."""

    class Meta:
        """Factory settings."""

        model = Fondo

    factura = SubFactory(FacturaClienteFactory)
    moneda = Faker('random_element', elements=[row[0] for row in MONEDAS])
    monto = Faker('pydecimal', max_value=10000, positive=True, right_digits=2)
    monto_disponible = factory.LazyAttribute(lambda o: o.monto)
    disponible = Faker('pybool')


class FonodoFactoryData:
    """ClienteFactoryData model."""

    def __init__(self):

        FondoDictFactory = generate_dict_factory(FondoFactory)
        self.data = FondoDictFactory()

    def build(self):
        """Building data for forms."""
        return self.data
