"""Comando para agregar múltiples permisos."""

# Django
from django.core.management.base import BaseCommand

# Models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    """Clase command."""

    help = 'Agrega permisos'

    def handle(self, *args, **kwargs):
        """Controlador del comandos."""

        counter = 0
        try:
            permissions = [
                # Listados
                {'name': 'Puede listar Archivos', 'codename': 'list_archivo',
                 'content_type': ContentType.objects.get(model='archivo')},
                {'name': 'Puede listar Clientes', 'codename': 'list_cliente',
                 'content_type': ContentType.objects.get(app_label='core', model='cliente')},
                {'name': 'Puede listar Cobranzas', 'codename': 'list_cobranza',
                 'content_type': ContentType.objects.get(model='cobranza')},
                {'name': 'Puede listar Facturas A Clientes', 'codename': 'list_factura',
                 'content_type': ContentType.objects.get(model='factura')},
                {'name': 'Puede listar Facturas A Proveedores', 'codename': 'list_facturaproveedor',
                 'content_type': ContentType.objects.get(model='facturaproveedor')},
                {'name': 'Puede listar Grupos', 'codename': 'list_group',
                 'content_type': ContentType.objects.get(model='group')},
                {'name': 'Puede listar Medios De Pagos', 'codename': 'list_mediopago',
                 'content_type': ContentType.objects.get(model='mediopago')},
                {'name': 'Puede listar Órdenes De Compras', 'codename': 'list_ordencompra',
                 'content_type': ContentType.objects.get(model='ordencompra')},
                {'name': 'Puede listar Pagos', 'codename': 'list_pago',
                 'content_type': ContentType.objects.get(model='pago')},
                {'name': 'Puede listar Permisos', 'codename': 'list_permission',
                 'content_type': ContentType.objects.get(model='permission')},
                {'name': 'Puede listar Proveedores', 'codename': 'list_proveedor',
                 'content_type': ContentType.objects.get(model='proveedor')},
                {'name': 'Puede listar Usuarios', 'codename': 'list_user',
                 'content_type': ContentType.objects.get(model='user')},
                # Reportes
                {'name': 'Puede ver reportes de Facturas A Clientes', 'codename': 'view_reports_factura',
                 'content_type': ContentType.objects.get(model='factura')},
                {'name': 'Puede ver reportes de Facturas A Proveedores', 'codename': 'view_reports_facturaproveedor',
                 'content_type': ContentType.objects.get(model='facturaproveedor')},
            ]

            for permission in permissions:
                if not Permission.objects.filter(codename=permission.get('codename')).exists():
                    Permission.objects.create(**permission)
                    counter += 1
            print('Se agregaron {} permisos nuevos.'.format(counter))
        except ContentType.DoesNotExist as err:
            print(err)
