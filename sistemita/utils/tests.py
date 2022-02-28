"""Commons functions for Tests."""

import logging
import random
from functools import partial
from typing import Any, Dict

# Django
from django.contrib.auth.models import Permission
from django.test import TestCase
from factory import Factory
from factory.base import StubObject

# Sistemita
from sistemita.authorization.models import User


def generate_dict_factory(factory: Factory):
    """Genera un objecto diccionario con los datos generado atravéz de Factory."""

    def convert_dict_from_stub(stub: StubObject) -> Dict[str, Any]:
        stub_dict = stub.__dict__
        for key, value in stub_dict.items():
            if isinstance(value, StubObject):
                stub_dict[key] = convert_dict_from_stub(value)
        return stub_dict

    def dict_factory(factory, **kwargs):
        stub = factory.stub(**kwargs)
        stub_dict = convert_dict_from_stub(stub)
        return stub_dict

    return partial(dict_factory, factory)


def rand_element_from_array(array):
    """Devuelve un elemento random de un array."""
    return random.choice(array)


def rand_range(_min, _max):
    """Genera un número dentro de un rango."""
    return random.randint(_min, _max)


def randN(length):
    """Devuelve un numero random de una longitud especifica."""

    _min = pow(10, length - 1)
    _max = pow(10, length) - 1
    return random.randint(_min, _max)


def prevent_request_warnings(original_function):
    """
    If we need to test for 404s or 405s this decorator can prevent the
    request class from throwing warnings.
    """

    def new_function(*args, **kwargs):
        # raise logging level to ERROR
        logger = logging.getLogger('django.request')
        previous_logging_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

        # trigger original function that would throw warning
        original_function(*args, **kwargs)

        # lower logging level back to previous
        logger.setLevel(previous_logging_level)

    return new_function


class BaseTestCase(TestCase):
    """BaseTestCase."""

    def assertHasProp(self, obj, prop):
        """Verifica si el objeto tiene una propiedad."""
        self.assertTrue(True if prop in obj else False)

    def assertHasProps(self, obj, props):
        """Verifica si el objeto tiene todas las propiedades."""
        for prop in props:
            self.assertHasProp(obj, prop)

    def assertHasErrorDetail(self, element, msg):
        """Verifica el mensaje."""
        self.assertEqual(element[0], msg)

    def create_superuser(self):
        """Crea un super usuario."""
        user = User.objects.create(username='admin')
        user.set_password('admin123')
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

    def create_user(self, permissions=[], **kwargs):
        """Crea un usuario que puede tener permisos."""
        user = User.objects.create(username='user', **kwargs)
        user.set_password('user12345')

        for row in permissions:
            permission = Permission.objects.filter(codename=row).first()
            if permission:
                user.user_permissions.add(permission)

        user.is_active = True
        user.save()
        return user

    @staticmethod
    def get_required_fields(model):
        """Retorna un listado con los campos requeridos de un modelo."""
        fields = model._meta.get_fields()
        required_fields = [f.name for f in fields if getattr(f, 'blank', False)]
        required_fields.remove('id')
        required_fields.remove('creado')
        required_fields.remove('modificado')
        return required_fields
