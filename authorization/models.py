"""Modelos del módulo Autentication."""

# Django
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType


class User(AbstractUser):
    """Modelo Usuario."""

    pass

    @property
    def full_name(self):
        """Retorna el nombre completo del usuario."""
        if self.last_name and self.first_name:
            return f'{self.last_name} {self.first_name}'
        elif self.first_name:
            return self.first_name
        else:
            return self.username


def permission_string_method(self):
    """Devuelve un string del modelo personalizado y traducido."""
    return '%s' % (self.name)


def contentype_string_method(self):
    """Devuelve un string del modelo personalizado y traducido."""
    return '%s' % (self.name.title())


Permission.__str__ = permission_string_method
ContentType.__str__ = contentype_string_method
