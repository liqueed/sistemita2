"""Group factories."""

# Models
from django.contrib.auth.models import Group

# Fake
from factory.django import DjangoModelFactory
from faker import Faker

# Sistemita
from sistemita.authorization.models import ContentType, Permission
from sistemita.utils.tests import rand_range

fake = Faker('es_ES')


class GroupFactory(DjangoModelFactory):
    """Fabrica de grupos."""

    name = fake.name()

    class Meta:
        """Factory settings."""

        model = Group
        django_get_or_create = ('name',)


class GroupFactoryData:
    """UserFactoryData model."""

    def __init__(self):
        limit = rand_range(1, 10)

        content_type_ids = [
            row
            for row in ContentType.objects.filter(
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
            ).values_list('pk', flat=True)
        ]

        permissions = [
            p
            for p in Permission.objects.filter(content_type_id__in=content_type_ids)
            .order_by('?')[:limit]
            .values_list('pk', flat=True)
        ]

        self.data = {
            'name': fake.name(),
            'permissions': permissions,
        }

    def build(self):
        """Building data for forms."""
        return self.data
