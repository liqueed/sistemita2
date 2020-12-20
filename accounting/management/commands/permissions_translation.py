"""Comandos útiles del módulo accounting."""

# Django
from django.core.management.base import BaseCommand

# Models
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    """Clase command."""

    help = 'Traduce  los nombres de los permisos'

    def handle(self, *args, **kwargs):
        """Controlador del comandos."""
        permissions = Permission.objects.filter(
            content_type__app_label__in=['accounting', 'auth', 'authorization', 'core']
        )
        app_name = ''

        for permission in permissions:
            name = permission.name

            if 'group' in name.lower():
                name = '{} grupo'.format(name[:-6])
            elif 'permission' in name.lower():
                name = '{} permiso'.format(name[:-11])
            elif 'user' in name.lower():
                name = '{} usuario'.format(name[:-5])

            if 'Can add' in name:
                app_name = name[8:]
                last_letter = app_name[-1]
                if last_letter in ['a', 'e', 'i', 'o', 'u', 'y']:
                    name = 'Puede agregar {}s'.format(app_name.title())
                else:
                    name = 'Puede agregar {}es'.format(app_name.title())
            elif 'Can view' in name:
                app_name = name[9:]
                last_letter = app_name[-1]
                if last_letter in ['a', 'e', 'i', 'o', 'u', 'y']:
                    name = 'Puede ver {}s'.format(app_name.title())
                else:
                    name = 'Puede ver {}es'.format(app_name.title())
            elif 'Can change' in name:
                app_name = name[11:]
                last_letter = app_name[-1]
                if last_letter in ['a', 'e', 'i', 'o', 'u', 'y']:
                    name = 'Puede editar {}s'.format(app_name.title())
                else:
                    name = 'Puede editar {}es'.format(app_name.title())
            elif 'Can delete' in name:
                app_name = name[11:]
                last_letter = app_name[-1]
                if last_letter in ['a', 'e', 'i', 'o', 'u', 'y']:
                    name = 'Puede eliminar {}s'.format(app_name.title())
                else:
                    name = 'Puede eliminar {}es'.format(app_name.title())

            if app_name:
                Permission.objects.filter(pk=permission.pk).update(
                    name=name
                )
