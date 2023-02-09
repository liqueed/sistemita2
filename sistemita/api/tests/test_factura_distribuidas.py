"""Factura distribuida de Facturas de Clientes API test."""

# Django
from django.core.management import call_command
from rest_framework.test import APIClient

# Sistemita
from sistemita.core.tests.factories import (
    FacturaDistribuidaFactory,
    FacturaDistribuidaFactoryData,
)
from sistemita.utils.tests import (
    BaseTestCase,
    prevent_request_warnings,
    rand_range,
)


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class FacturaDistribuidaListViewAPITestCase(BaseTestCase):
    """Tests sobre la API de facturas a clientes."""

    def setUp(self):
        self.client = APIClient()

    def test_factura_distribuida_list_with_user_authenticated(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/api/factura-distribuida/')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_factura_distribuida_list_with_user_anonymous(self):
        """Verifica que el usuario sin acceso no pueda listar."""
        request = self.client.get('/api/factura-distribuida/')
        self.assertEqual(request.status_code, 403)

    def test_factura_distribuida_list_length(self):
        """Verifica que devuelva un listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        limit = rand_range(1, 10)
        FacturaDistribuidaFactory.create_batch(limit)
        request = self.client.get('/api/factura-distribuida/')
        self.assertEqual(len(request.json()), limit)

    def test_factura_distribuida_list_empty(self):
        """Verifica que devuelva un listado vacío."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        request = self.client.get('/api/factura-distribuida/')
        self.assertEqual(len(request.json()), 0)


class FacturaDistribuidaRetrieveViewAPITestCase(BaseTestCase):
    """Tests sobre el detalle de la API de facturas distribuidas."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_with_user_authenticated(self):
        """Verifica que el usuario con permisos pueda acceder al detalle de una instancia."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaDistribuidaFactory.create()
        response = self.client.get(f'/api/factura-distribuida/{factura.pk}/')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_retrieve_with_user_anonymous(self):
        """Verifica que el usuario sin acceso no pueda acceder al detalle de una instancia."""
        factura = FacturaDistribuidaFactory.create()
        request = self.client.get(f'/api/factura-distribuida/{factura.pk}/')
        self.assertEqual(request.status_code, 403)

    def test_retrieve(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaDistribuidaFactory.create()
        request = self.client.get(f'/api/factura-distribuida/{factura.pk}/')
        self.assertEqual(request.status_code, 200)

    @prevent_request_warnings
    def test_retrieve_not_found(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        random = rand_range(1, 100)
        request = self.client.get(f'/api/factura-distribuida/{random}/')
        self.assertEqual(request.status_code, 404)

    def test_retrieve_fields(self):
        """Verifica los campos devueltos del detalle."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura = FacturaDistribuidaFactory.create()
        request = self.client.get(f'/api/factura-distribuida/{factura.pk}/')
        fields = ['id', 'factura', 'monto_distribuido', 'factura_distribuida_proveedores']
        self.assertHasProps(request.json(), fields)


class FacturaDistribuidaCreateViewAPITestCase(BaseTestCase):
    """Tests sobre la vista de crear."""

    def setUp(self):
        self.client = APIClient()
        self.data_create = FacturaDistribuidaFactoryData().create()

    def test_validate_data(self):
        """Valida que si los datos son correcto agregue la instancia."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/factura-distribuida/', self.data_create, format='json')
        self.assertEqual(response.status_code, 201)
