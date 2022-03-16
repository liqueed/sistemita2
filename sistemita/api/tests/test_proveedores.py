"""Proveedores API test."""

# Django
from django.core.management import call_command
from rest_framework.test import APIClient

# Sistemita
from sistemita.core.tests.factories import ProveedorFactory
from sistemita.utils.tests import (
    BaseTestCase,
    prevent_request_warnings,
    rand_range,
)


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class ProveedorListAPITestCase(BaseTestCase):
    """Test sobre el listado de la API de proveedores."""

    def setUp(self):
        self.client = APIClient()

    def test_proveedores_list_with_user_authenticated(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/api/proveedor/')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_proveedor_list_with_user_anonymous(self):
        """Verifica que el usuario sin acceso no pueda listar."""
        request = self.client.get('/api/proveedor/')
        self.assertEqual(request.status_code, 403)

    def test_proveedor_list_length(self):
        """Verifica que devuelva un listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        limit = rand_range(1, 10)
        ProveedorFactory.create_batch(limit)
        request = self.client.get('/api/proveedor/')
        self.assertEqual(len(request.json()), limit)

    def test_proveedor_list_empty(self):
        """Verifica que devuelva un listado vacío."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        request = self.client.get('/api/proveedor/')
        self.assertEqual(len(request.json()), 0)

    def test_proveedor_list_search_by_razon_social(self):
        """Verifica que devuelva resultados al filtra por razón social."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        proveedor = ProveedorFactory.create()
        request = self.client.get(f'/api/proveedor/?razon_social__cuit__icontains={proveedor.razon_social.lower()}')
        self.assertEqual(len(request.json()), 1)
        request = self.client.get(f'/api/proveedor/?razon_social__cuit__icontains={proveedor.razon_social.upper()}')
        self.assertEqual(len(request.json()), 1)


class FacturaImputadaRetrieveViewAPITestCase(BaseTestCase):
    """Tests sobre el detalle de la API de proveedor."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_with_user_authenticated(self):
        """Verifica que el usuario con permisos pueda acceder al detalle de una instancia."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        proveedor = ProveedorFactory.create()
        response = self.client.get(f'/api/proveedor/{proveedor.pk}/')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_retrieve_with_user_anonymous(self):
        """Verifica que el usuario sin acceso no pueda acceder al detalle de una instancia."""
        proveedor = ProveedorFactory.create()
        request = self.client.get(f'/api/proveedor/{proveedor.pk}/')
        self.assertEqual(request.status_code, 403)

    def test_retrieve(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        proveedor = ProveedorFactory.create()
        request = self.client.get(f'/api/proveedor/{proveedor.pk}/')
        self.assertEqual(request.status_code, 200)

    @prevent_request_warnings
    def test_not_found(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        random = rand_range(1, 100)
        request = self.client.get(f'/api/proveedor/{random}/')
        self.assertEqual(request.status_code, 404)

    def test_proveedor_retrieve_fields(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        proveedor = ProveedorFactory.create()
        request = self.client.get(f'/api/proveedor/{proveedor.pk}/')
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
            'cbu',
        ]
        self.assertHasProps(request.json(), fields)
