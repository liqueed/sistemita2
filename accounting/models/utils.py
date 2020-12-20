"""Modelos utilitarios."""

# Models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def permission_string_method(self):
    """Devuelve un string del modelo personalizado y traducido."""
    return '%s' % (self.name)


def contentype_string_method(self):
    """Devuelve un string del modelo personalizado y traducido."""
    return '%s' % (self.name.title())


Permission.__str__ = permission_string_method
ContentType.__str__ = contentype_string_method
