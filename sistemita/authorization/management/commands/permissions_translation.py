"""Comando para traducir los nombres de los permisos que vienen por defecto en Django."""

# Django
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Clase command."""

    help = 'Traduce  los nombres de los permisos'

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        """Controlador del comandos."""

        permissions = Permission.objects.filter(
            content_type__app_label__in=['accounting', 'auth', 'authorization', 'core']
        )

        for permission in permissions:
            name = permission.name

            if 'group' in name.lower():
                name = '{} grupo'.format(name[:-6])
            elif 'permission' in name.lower():
                name = '{} permiso'.format(name[:-11])
            elif 'user' in name.lower():
                name = '{} usuario'.format(name[:-5])

            if 'Can add' in name:
                name = self.change_app_name(name, 8, 'Puede agregar')
            elif 'Can view' in name:
                name = self.change_app_name(name, 9, 'Puede ver')
            elif 'Can change' in name:
                name = self.change_app_name(name, 11, 'Puede editar')
            elif 'Can delete' in name:
                name = self.change_app_name(name, 11, 'Puede eliminar')

            if name:
                Permission.objects.filter(pk=permission.pk).update(name=name)

        self.stdout.write(self.style.SUCCESS(f'Permisos traducidos exitosamente.'))

    def change_app_name(self, name, start, translation):
        """Traduce nombre del permiso según una acción dada."""
        try:
            app_name = name[start:]

            if app_name == 'factura':
                app_name = 'facturas a cliente'
            elif app_name == 'factura proveedor':
                app_name = 'facturas a proveedor'
            elif app_name == 'medio de pago':
                app_name = 'medios de pago'
            elif app_name == 'orden de compra':
                app_name = 'órdenes de compra'

            last_letter = app_name[-1]
            if last_letter in ['a', 'e', 'i', 'o', 'u', 'y']:
                name = '{} {}s'.format(translation, app_name.title())
            else:
                name = '{} {}es'.format(translation, app_name.title())
            return name
        except Exception:  # pylint: disable=broad-except
            return False
