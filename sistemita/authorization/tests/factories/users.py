"""User factories."""

# Fake
from factory.django import DjangoModelFactory
from faker import Faker

# Sistemita
from sistemita.authorization.models import User

fake = Faker('es_ES')


class UserFactory(DjangoModelFactory):
    """Fabrica de usuarios."""

    class Meta:
        """Factory settings."""

        model = User
        django_get_or_create = ('username', 'email')

    first_name = fake.first_name()
    last_name = fake.last_name()
    username = fake.simple_profile().get('username')
    email = fake.simple_profile().get('mail')
    password = fake.password()
    is_active = True


class UserAdminFactory(UserFactory):
    """Fabrica de usuarios administradores."""

    is_superuser = True


class UserFactoryData:
    """UserFactoryData model."""

    def __init__(self):

        self._password = fake.password()
        self.data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'username': fake.simple_profile().get('username'),
            'email': fake.simple_profile().get('mail'),
            'password': self._password,
            'password_confirmation': self._password,
            'is_active': True,
        }

    def build(self):
        """Building data for forms."""
        return self.data
