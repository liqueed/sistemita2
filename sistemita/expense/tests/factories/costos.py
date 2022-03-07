"""Costo factories."""

# Fake
import factory
from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker as Fake

# Sistemita
from sistemita.expense.models import Costo
from sistemita.expense.tests.factories.fondos import FondoFactory
from sistemita.utils.tests import generate_dict_factory

fake = Fake()


class CostoFactory(DjangoModelFactory):
    """Fabrica de instancias del modelo de fondos."""

    class Meta:
        """Factory settings."""

        model = Costo

    fondo = SubFactory(FondoFactory)

    fecha = Faker('date_this_month')
    descripcion = Faker('text', max_nb_chars=50)
    moneda = factory.LazyAttribute(lambda o: o.fondo.moneda)
    monto = factory.LazyAttribute(lambda o: o.fondo.monto)


class CostoFactoryData:
    """CostoFactoryData model."""

    def __init__(self):

        CostoDictFactory = generate_dict_factory(CostoFactory)
        self.data = CostoDictFactory()

        fondo = FondoFactory.create()
        self.data_create = {
            'fondo': fondo.pk,
            'fecha': fake.date_this_month(),
            'descripcion': fake.text(),
            'moneda': fondo.moneda,
            'monto': float(fondo.monto),
        }

    def build(self):
        """Building data for forms."""
        return self.data

    def create(self):
        """Devuelve un diccionario con datos."""
        return self.data_create
