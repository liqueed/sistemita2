"""Modelos del módulo Autentication."""

# Django
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Utils
from sistemita.utils.strings import MESSAGE_ERROR_EMAIL_UNIQUE


class User(AbstractUser):
    """Modelo Usuario."""

    email = models.EmailField('email', unique=True, error_messages={'unique': MESSAGE_ERROR_EMAIL_UNIQUE})

    @property
    def full_name(self):
        """Retorna el nombre completo del usuario."""
        if self.last_name and self.first_name:
            return f'{self.last_name} {self.first_name}'
        if self.first_name:
            return self.first_name
        return self.username


def permission_string_method(self):
    """Devuelve un string del modelo personalizado y traducido."""
    return f'{self.name}'


def contentype_string_method(self):
    """Devuelve un string del modelo personalizado y traducido."""
    return f'{self.name.title()}'


Permission.__str__ = permission_string_method
ContentType.__str__ = contentype_string_method
