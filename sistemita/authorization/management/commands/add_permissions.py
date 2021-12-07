"""Comando para agregar múltiples permisos."""

# Django
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Clase command."""

    help = 'Agrega permisos'

    def handle(self, *args, **kwargs):
        """Controlador del comandos."""

        counter = 0
        try:
            permissions = [
                # Listados
                {
                    'name': 'Puede listar Archivos',
                    'codename': 'list_archivo',
                    'content_type': ContentType.objects.get(model='archivo'),
                },
                {
                    'name': 'Puede listar Clientes',
                    'codename': 'list_cliente',
                    'content_type': ContentType.objects.get(app_label='core', model='cliente'),
                },
                {
                    'name': 'Puede listar Cobranzas',
                    'codename': 'list_cobranza',
                    'content_type': ContentType.objects.get(model='cobranza'),
                },
                {
                    'name': 'Puede listar Facturas A Clientes',
                    'codename': 'list_factura',
                    'content_type': ContentType.objects.get(model='factura'),
                },
                {
                    'name': 'Puede listar Facturas imputadas',
                    'codename': 'list_facturaimputada',
                    'content_type': ContentType.objects.get(model='facturaimputada'),
                },
                {
                    'name': 'Puede listar Categoría de Facturas',
                    'codename': 'list_facturacategoria',
                    'content_type': ContentType.objects.get(model='facturacategoria'),
                },
                {
                    'name': 'Puede listar Facturas A Proveedores',
                    'codename': 'list_facturaproveedor',
                    'content_type': ContentType.objects.get(model='facturaproveedor'),
                },
                {
                    'name': 'Puede listar Facturas imputadas de Proveedores',
                    'codename': 'list_facturaproveedorimputada',
                    'content_type': ContentType.objects.get(model='facturaproveedorimputada'),
                },
                {
                    'name': 'Puede listar Grupos',
                    'codename': 'list_group',
                    'content_type': ContentType.objects.get(model='group'),
                },
                {
                    'name': 'Puede listar Medios De Pagos',
                    'codename': 'list_mediopago',
                    'content_type': ContentType.objects.get(model='mediopago'),
                },
                {
                    'name': 'Puede listar Órdenes De Compras',
                    'codename': 'list_ordencompra',
                    'content_type': ContentType.objects.get(model='ordencompra'),
                },
                {
                    'name': 'Puede listar Pagos',
                    'codename': 'list_pago',
                    'content_type': ContentType.objects.get(model='pago'),
                },
                {
                    'name': 'Puede listar Permisos',
                    'codename': 'list_permission',
                    'content_type': ContentType.objects.get(model='permission'),
                },
                {
                    'name': 'Puede listar Proveedores',
                    'codename': 'list_proveedor',
                    'content_type': ContentType.objects.get(model='proveedor'),
                },
                {
                    'name': 'Puede listar Usuarios',
                    'codename': 'list_user',
                    'content_type': ContentType.objects.get(model='user'),
                },
                # Reportes
                {
                    'name': 'Puede ver reportes de Facturas A Clientes',
                    'codename': 'view_reports_factura',
                    'content_type': ContentType.objects.get(model='factura'),
                },
                {
                    'name': 'Puede ver reportes de Facturas A Proveedores',
                    'codename': 'view_reports_facturaproveedor',
                    'content_type': ContentType.objects.get(model='facturaproveedor'),
                },
                {
                    'name': 'Puede ver reporte de ventas',
                    'codename': 'view_report_sales_facturaproveedor',
                    'content_type': ContentType.objects.get(model='facturaproveedor'),
                },
                # Facturas a clientes
                {
                    'name': 'Puede editar número de Facturas A Clientes',
                    'codename': 'change_nro_factura',
                    'content_type': ContentType.objects.get(model='factura'),
                },
                {
                    'name': 'Puede editar neto de Facturas A Clientes',
                    'codename': 'change_neto_factura',
                    'content_type': ContentType.objects.get(model='factura'),
                },
                {
                    'name': 'Puede editar iva de Facturas A Clientes',
                    'codename': 'change_iva_factura',
                    'content_type': ContentType.objects.get(model='factura'),
                },
                {
                    'name': 'Puede editar total de Facturas A Clientes',
                    'codename': 'change_total_factura',
                    'content_type': ContentType.objects.get(model='factura'),
                },
                {
                    'name': 'Puede editar archivos de Facturas A Clientes',
                    'codename': 'change_archivos_factura',
                    'content_type': ContentType.objects.get(model='factura'),
                },
                # Facturas a proveedores
                {
                    'name': 'Puede editar número de Facturas A Proveedores',
                    'codename': 'change_nro_facturaproveedor',
                    'content_type': ContentType.objects.get(model='facturaproveedor'),
                },
                {
                    'name': 'Puede editar neto de Facturas A Proveedores',
                    'codename': 'change_neto_facturaproveedor',
                    'content_type': ContentType.objects.get(model='facturaproveedor'),
                },
                {
                    'name': 'Puede editar iva de Facturas A Proveedores',
                    'codename': 'change_iva_facturaproveedor',
                    'content_type': ContentType.objects.get(model='facturaproveedor'),
                },
                {
                    'name': 'Puede editar total de Facturas A Proveedores',
                    'codename': 'change_total_facturaproveedor',
                    'content_type': ContentType.objects.get(model='facturaproveedor'),
                },
                {
                    'name': 'Puede editar archivos de Facturas A Proveedores',
                    'codename': 'change_archivos_facturaproveedor',
                    'content_type': ContentType.objects.get(model='facturaproveedor'),
                },
                # Pagos
                {
                    'name': 'Puede exportar retenciones de pagos a Proveedores',
                    'codename': 'view_report_retencion_pago',
                    'content_type': ContentType.objects.get(model='pago'),
                },
                # Módulo de mis facturas de proveedor
                {
                    'name': 'Puede ver módulo Mis facturas',
                    'codename': 'view_mis_facturasproveedor',
                    'content_type': ContentType.objects.get(model='facturaproveedor'),
                },
            ]

            for permission in permissions:
                if not Permission.objects.filter(codename=permission.get('codename')).exists():
                    Permission.objects.create(**permission)
                    counter += 1
            self.stdout.write(self.style.SUCCESS(f'Se agregaron {counter} permisos nuevos.'))
        except ContentType.DoesNotExist as err:
            self.stdout.write(self.style.ERROR(err))
