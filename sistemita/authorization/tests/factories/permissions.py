"""Permissions factories."""

# Fake
from factory.django import DjangoModelFactory
from faker import Faker

# Sistemita
from sistemita.authorization.models import ContentType, Permission

fake = Faker('es_ES')


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

    name = fake.name()
    content_type = content_type
    codename = fake.name().replace(' ', '_').lower()


class PermissionFactoryData:
    """PermissionFactoryData model."""

    def __init__(self):

        self.data = {
            'name': fake.name(),
            'content_type': content_type.pk,
            'codename': fake.name().replace(' ', '_').lower(),
        }

    def build(self):
        """Building data for forms."""
        return self.data
