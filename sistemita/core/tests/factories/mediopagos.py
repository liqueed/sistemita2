"""Core factories."""

from factory import Faker
from factory.django import DjangoModelFactory

# Sistemita
from sistemita.core.models import MedioPago
from sistemita.utils.tests import generate_dict_factory


class MedioPagoFactory(DjangoModelFactory):
    """Medio de pago factory que herada de DjangoModelFactory."""

    class Meta:
        """Factory settings."""

        model = MedioPago
        django_get_or_create = ('nombre',)

    nombre = Faker(
        'random_element',
        elements=(
            'Cheque',
            'Efectivo',
            'Imputación interna',
            'Mercado pago',
            'Paypal',
            'Tarjeta de crédito',
            'Transferencia',
        ),
    )


class MedioPagoFactoryData:
    """Creación de datos para el modelo de Medio de pagos."""

    def __init__(self):
        MedioFactoryDictFactory = generate_dict_factory(MedioPagoFactory)
        self.data = MedioFactoryDictFactory()

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data
