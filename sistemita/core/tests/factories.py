"""Core factories."""

from factory.django import DjangoModelFactory
from faker import Faker

# Sistemita
from sistemita.core.models import Cliente, Distrito, Localidad, Provincia
from sistemita.utils.tests import randN

fake = Faker('es_ES')


class ClienteFactory(DjangoModelFactory):
    """Fabrica de datos de cliente."""

    razon_social = fake.name()
    cuit = randN(11)
    correo = fake.email()
    telefono = fake.phone_number()[0:14]
    calle = fake.name()[0:35]
    numero = fake.numerify(text='##@@')
    piso = fake.numerify(text='#@')
    dpto = fake.lexify(text='?')

    class Meta:
        """Factory settings."""

        model = Cliente


class ClienteFactoryData:
    """ClienteFactoryData model."""

    def __init__(self):

        provincia = Provincia.objects.order_by('?').first()
        distrito = Distrito.objects.filter(provincia=provincia).order_by('?').first()
        localidad = Localidad.objects.filter(distrito=distrito).order_by('?').first()

        self.data = {
            'razon_social': fake.name(),
            'cuit': randN(11),
            'correo': fake.email(),
            'telefono': fake.phone_number()[0:14],
            'calle': fake.name()[0:35],
            'numero': fake.numerify(text='##@@'),
            'piso': fake.numerify(text='#@'),
            'dpto': fake.lexify(text='?'),
            'provincia': provincia.pk,
            'distrito': distrito.pk,
            'localidad': localidad.pk,
        }

    def build(self):
        """Building data to forms."""
        return self.data
