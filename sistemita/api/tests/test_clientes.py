"""Clientes API test."""

# Django
from django.core.management import call_command
from rest_framework.test import APIClient

# Sistemita
from sistemita.core.tests.factories import ClienteFactory
from sistemita.utils.tests import (
    BaseTestCase,
    prevent_request_warnings,
    rand_range,
)


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class ClienteAPITestCase(BaseTestCase):
    """Tests sobre la API de clientes."""

    def setUp(self):
        self.client = APIClient()

    def test_cliente_list_with_user_authenticated(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/api/cliente/')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_cliente_list_with_user_anonymous(self):
        """Verifica que el usuario sin acceso no pueda listar."""
        request = self.client.get('/api/cliente/')
        self.assertEqual(request.status_code, 403)

    def test_cliente_list_length(self):
        """Verifica que devuelva un listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        limit = rand_range(1, 10)
        ClienteFactory.create_batch(limit)
        request = self.client.get('/api/cliente/')
        self.assertEqual(len(request.json()), limit)

    def test_cliente_list_empty(self):
        """Verifica que devuelva un listado vacío."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        request = self.client.get('/api/cliente/')
        self.assertEqual(len(request.json()), 0)

    def test_cliente_list_search_by_razon_social(self):
        """Verifica que devuelva resultados al filtra por razón social."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        cliente = ClienteFactory.create()
        request = self.client.get(f'/api/cliente/?razon_social__cuit__icontains={cliente.razon_social.lower()}')
        self.assertEqual(len(request.json()), 1)
        request = self.client.get(f'/api/cliente/?razon_social__cuit__icontains={cliente.razon_social.upper()}')
        self.assertEqual(len(request.json()), 1)

    def test_cliente_retrieve(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        cliente = ClienteFactory.create()
        request = self.client.get(f'/api/cliente/{cliente.pk}/')
        self.assertEqual(request.status_code, 200)

    @prevent_request_warnings
    def test_cliente_retrieve_not_found(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        random = rand_range(1, 100)
        request = self.client.get(f'/api/cliente/{random}/')
        self.assertEqual(request.status_code, 404)

    def test_cliente_retrieve_fields(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        cliente = ClienteFactory.create()
        request = self.client.get(f'/api/cliente/{cliente.pk}/')
        fields = [
            'id',
            'razon_social',
            'cuit',
            'correo',
            'telefono',
            'calle',
            'numero',
            'piso',
            'dpto',
            'provincia',
            'distrito',
            'localidad',
            'tipo_envio_factura',
            'link_envio_factura',
            'correo_envio_factura',
        ]
        self.assertHasProps(request.json(), fields)
