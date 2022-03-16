"""Factura de Proveedores API test."""

# Django
from django.core.management import call_command
from rest_framework.test import APIClient

# Sistemita
from sistemita.core.tests.factories import FacturaProveedorFactory
from sistemita.utils.tests import (
    BaseTestCase,
    prevent_request_warnings,
    rand_range,
)


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class FacturaProveedorListViewAPITestCase(BaseTestCase):
    """Tests sobre el listado de la API de facturas de proveedores."""

    def setUp(self):
        self.client = APIClient()

    def test_factura_proveedor_list_with_user_authenticated(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/api/factura-proveedor/')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_factura_proveedor_list_with_user_anonymous(self):
        """Verifica que el usuario sin acceso no pueda listar."""
        request = self.client.get('/api/factura-proveedor/')
        self.assertEqual(request.status_code, 403)

    def test_factura_proveedor_list_length(self):
        """Verifica que devuelva un listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        limit = rand_range(1, 10)
        FacturaProveedorFactory.create_batch(limit)
        request = self.client.get('/api/factura-proveedor/')
        self.assertEqual(len(request.json()), limit)

    def test_factura_proveedor_list_empty(self):
        """Verifica que devuelva un listado vacío."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        request = self.client.get('/api/factura-proveedor/')
        self.assertEqual(len(request.json()), 0)

    def test_factura_proveedor_list_search_by_cliente(self):
        """Verifica que devuelva resultados al filtra por ID de cliente."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaProveedorFactory.create()
        request = self.client.get(f'/api/factura-proveedor/?proveedor={factura.proveedor.pk}')
        self.assertEqual(len(request.json()), 1)

    def test_factura_proveedor_list_search_by_cobrado(self):
        """Verifica que devuelva resultados al filtra por factura cobrado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaProveedorFactory.create()
        request = self.client.get(f'/api/factura-proveedor/?cobrado={factura.cobrado}')
        self.assertEqual(len(request.json()), 1)

    def test_factura_proveedor_list_search_by_numero(self):
        """Verifica que devuelva resultados al filtra por número de factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaProveedorFactory.create()
        request = self.client.get(f'/api/factura-proveedor/?numero__icontains={factura.numero}')
        self.assertEqual(len(request.json()), 1)

    def test_factura_proveedor_list_search_by_tipo(self):
        """Verifica que devuelva resultados al filtra por tipo de factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaProveedorFactory.create()
        request = self.client.get(f'/api/factura-proveedor/?tipo__startswith={factura.tipo}')
        self.assertEqual(len(request.json()), 1)

    def test_factura_proveedor_list_search_all_filters(self):
        """Verifica que devuelva resultados utilizando todos los filtros."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaProveedorFactory.create()
        request = self.client.get(
            f'''/api/factura-proveedor/?proveedor={factura.proveedor.pk}&cobrado={factura.cobrado}&
            numero__icontains={factura.numero}&tipo__startswith={factura.tipo}'''
        )
        self.assertEqual(len(request.json()), 1)


class FacturaProveeedorRetrieveAPITestCase(BaseTestCase):
    """Tests sobre el detalle de la API de factura de proveedores."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_with_user_authenticated(self):
        """Verifica que el usuario con permisos pueda acceder al detalle de una instancia."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaProveedorFactory.create()
        response = self.client.get(f'/api/factura-proveedor/{factura.pk}/')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_retrieve_with_user_anonymous(self):
        """Verifica que el usuario sin acceso no pueda acceder al detalle de una instancia."""
        factura = FacturaProveedorFactory.create()
        request = self.client.get(f'/api/factura-proveedor/{factura.pk}/')
        self.assertEqual(request.status_code, 403)

    def test_retrieve(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaProveedorFactory.create()
        request = self.client.get(f'/api/factura-proveedor/{factura.pk}/')
        self.assertEqual(request.status_code, 200)

    @prevent_request_warnings
    def test_retrieve_not_found(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        random = rand_range(1, 100)
        request = self.client.get(f'/api/factura-proveedor/{random}/')
        self.assertEqual(request.status_code, 404)

    def test_retrieve_fields(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaProveedorFactory.create()
        request = self.client.get(f'/api/factura-proveedor/{factura.pk}/')
        fields = ['id', 'fecha', 'numero', 'proveedor', 'tipo', 'moneda', 'neto', 'iva', 'cobrado', 'total', 'archivos']
        self.assertHasProps(request.json(), fields)
