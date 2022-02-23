"""Permissions factories."""

# Fake
from factory import Faker
from factory.django import DjangoModelFactory

# Sistemita
from sistemita.authorization.models import ContentType, Permission
from sistemita.utils.tests import generate_dict_factory

content_type = (
    ContentType.objects.filter(
        app_label__in=['accounting', 'auth', 'authorization', 'core', 'expense'],
        model__in=[
            'archivo',
            'cliente',
            'factura',
            'ordencompra',
            'cobranza',
            'proveedor',
            'facturaproveedor',
            'pago',
            'mediopago',
            'permission',
            'user',
            'group',
            'fondo',
            'costo',
        ],
    )
    .order_by('?')
    .first()
)


class PermissionFactory(DjangoModelFactory):
    """Fabrica de permisos."""

    class Meta:
        """Factory settings."""

        model = Permission
        django_get_or_create = ('content_type', 'codename')

    name = Faker('name')
    content_type = content_type
    codename = Faker('bothify', text='???_????_????')


class PermissionFactoryData:
    """PermissionFactoryData model."""

    def __init__(self):

        PermissionFactoryDictData = generate_dict_factory(PermissionFactory)
        self.data = PermissionFactoryDictData()
        self.data.update({'content_type': content_type.pk})

    def build(self):
        """Building data for forms."""
        return self.data
