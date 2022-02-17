"""User factories."""

# Fake
from factory import Faker
from factory.django import DjangoModelFactory

# Models
from sistemita.authorization.models import User
from sistemita.utils.tests import generate_dict_factory


class UserFactory(DjangoModelFactory):
    """Fabrica de usuarios."""

    class Meta:
        """Factory settings."""

        model = User
        django_get_or_create = ('username', 'email')

    first_name = Faker('first_name')
    last_name = Faker('last_name')
    username = Faker('user_name')
    email = Faker('email')
    password = Faker('password')
    is_active = True


class UserAdminFactory(UserFactory):
    """Fabrica de usuarios administradores."""

    is_superuser = True


class UserFactoryData:
    """UserFactoryData model."""

    def __init__(self):

        UserFactoryDictData = generate_dict_factory(UserFactory)
        self.data = UserFactoryDictData()
        self.data.update({'password_confirmation': self.data.get('password')})

    def build(self):
        """Building data for forms."""
        return self.data
