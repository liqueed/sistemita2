"""Core factories."""

from factory.django import DjangoModelFactory
from faker import Faker

# Sistemita
from sistemita.core.models import MedioPago
from sistemita.utils.tests import rand_element_from_array

fake = Faker('es_ES')


class MedioPagoFactoryData:
    """Creación de datos para el modelo de Medio de pagos."""

    _medios = [
        'Cheque',
        'Efectivo',
        'Imputación interna',
        'Mercado pago',
        'Paypal',
        'Tarjeta de crédito',
        'Transferencia',
    ]

    def __init__(self):
        self.nombre = rand_element_from_array(self._medios)
        self.data = {'nombre': self.nombre}

    def build(self):
        """Devuelve un diccionario con datos."""
        return self.data


class MedioPagoFactory(DjangoModelFactory):
    """Medio de pago factory que herada de DjangoModelFactory."""

    class Meta:
        """Factory settings."""

        model = MedioPago
        django_get_or_create = ('nombre',)

    nombre = MedioPagoFactoryData().nombre
