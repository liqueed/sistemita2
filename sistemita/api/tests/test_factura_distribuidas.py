"""Factura distribuida de Facturas de Clientes API test."""

# Django
from django.core import mail
from django.core.management import call_command
from rest_framework.test import APIClient

# Sistemita
from sistemita.core.models.cliente import FacturaDistribuida
from sistemita.core.tests.factories import (
    FacturaDistribuidaFactory,
    FacturaDistribuidaFactoryData,
    FacturaDistribuidaProveedorFactory,
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

    @prevent_request_warnings
    def test_validate_fields_required(self):
        """Valida los campos requeridos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/factura-distribuida/', {}, format='json')
        required_fields = ['factura_distribuida_id', 'distribucion_list']
        self.assertHasProps(response.data, required_fields)
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_invalid_field_proveedores(self):
        """Valida el id de proveedores."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        self.data_create['distribucion_list'][0]['id'] = 1000
        response = self.client.post('/api/factura-distribuida/', self.data_create, format='json')
        self.assertHasErrorDetail(response.data.get('distribucion_list'), 'El proveedor no existe.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_invalid_field_montos(self):
        """Valida el mensaje de error en caso de que los montos superen el monto de la factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        self.data_create['distribucion_list'][0]['monto'] += 1
        response = self.client.post('/api/factura-distribuida/', self.data_create, format='json')
        self.assertHasErrorDetail(
            response.data.get('distribucion_list'), 'Los montos no pueden superar al total de la factura.'
        )
        self.assertEqual(response.status_code, 400)

    def test_create_lenght_factura_distribuida_proveedor(self):
        """Valida la cantidad de instancia FacturaDistribuidaProveedor."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        len_distribucion_factura = len(self.data_create['distribucion_list'])
        response = self.client.post('/api/factura-distribuida/', self.data_create, format='json')
        factura_distribuida_id = response.data.get('factura_distribuida_id')
        factura_distribuida = FacturaDistribuida.objects.get(pk=factura_distribuida_id)
        self.assertEqual(factura_distribuida.factura_distribuida_proveedores.count(), len_distribucion_factura)

    def test_create_send_notification_to_proveedores(self):
        """Valida la cantidad de notificaciones enviadas, según la cantidad de proveedores."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/factura-distribuida/', self.data_create, format='json')
        len_distribucion = len(response.data['distribucion_list'])
        self.assertEqual(len(mail.outbox), len_distribucion)

    def test_factura_distribuida(self):
        """
        Valida que la factura quede marcada como distribuida si el monto distribuida es igual a la cant a distribuir.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/factura-distribuida/', self.data_create, format='json')
        factura_distribuida_id = response.data.get('factura_distribuida_id')
        factura_distribuida = FacturaDistribuida.objects.get(pk=factura_distribuida_id)
        self.assertTrue(factura_distribuida.distribuida)

    def test_factura_no_distribuida(self):
        """
        Valida que la factura quede marcada como no distribuida si el monto distribuidp es menor a la cant a distribuir.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        self.data_create['distribucion_list'][0]['monto'] -= 1
        response = self.client.post('/api/factura-distribuida/', self.data_create, format='json')
        factura_distribuida_id = response.data.get('factura_distribuida_id')
        factura_distribuida = FacturaDistribuida.objects.get(pk=factura_distribuida_id)
        self.assertFalse(factura_distribuida.distribuida)


class FacturaDistribuidaUpdateViewAPITestCase(BaseTestCase):
    """Tests sobre la vista de editar."""

    def setUp(self):
        self.client = APIClient()
        self.data_update = FacturaDistribuidaFactoryData().update()

    def test_validate_data(self):
        """Valida que si los datos son correcto agregue edita la instancia."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.put(
            f'/api/factura-distribuida/{self.data_update.get("factura_distribuida_id")}/',
            self.data_update,
            format='json',
        )
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_validate_fields_required(self):
        """Valida los campos requeridos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.put(
            f'/api/factura-distribuida/{self.data_update.get("factura_distribuida_id")}/', {}, format='json'
        )
        required_fields = ['factura_distribuida_id', 'distribucion_list']
        self.assertHasProps(response.data, required_fields)
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_invalid_field_proveedores(self):
        """Valida el id de proveedores."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        self.data_update['distribucion_list'][0]['id'] = 1000
        response = self.client.put(
            f'/api/factura-distribuida/{self.data_update.get("factura_distribuida_id")}/',
            self.data_update,
            format='json',
        )
        self.assertHasErrorDetail(response.data.get('distribucion_list'), 'El proveedor no existe.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_invalid_field_montos(self):
        """Valida el mensaje de error en caso de que los montos superen el monto de la factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        self.data_update['distribucion_list'][0]['monto'] += 1
        response = self.client.put(
            f'/api/factura-distribuida/{self.data_update.get("factura_distribuida_id")}/',
            self.data_update,
            format='json',
        )
        self.assertHasErrorDetail(
            response.data.get('distribucion_list'), 'Los montos no pueden superar al total de la factura.'
        )
        self.assertEqual(response.status_code, 400)

    def test_update_lenght_factura_distribuida_proveedor(self):
        """Valida la cantidad de instancia FacturaDistribuidaProveedor."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        len_distribucion_factura = len(self.data_update['distribucion_list'])
        response = self.client.put(
            f'/api/factura-distribuida/{self.data_update.get("factura_distribuida_id")}/',
            self.data_update,
            format='json',
        )
        factura_distribuida_id = response.data.get('factura_distribuida_id')
        factura_distribuida = FacturaDistribuida.objects.get(pk=factura_distribuida_id)
        self.assertEqual(factura_distribuida.factura_distribuida_proveedores.count(), len_distribucion_factura)

    def test_update_send_notification_to_proveedores(self):
        """Valida la cantidad de notificaciones enviadas al agregar una nueva distribución."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        distribucion_list = self.data_update['distribucion_list']
        monto = 0

        # Obtiene el monto total
        for item in distribucion_list:
            monto += item.get('monto')

        # Setea el nuevo monto
        new_monto = monto / (len(distribucion_list) + 1)
        for item in distribucion_list:
            item['monto'] = new_monto

        # Agrega un nuevo item
        self.data_update['distribucion_list'].append(
            {
                'id': self.data_update['distribucion_list'][0]['id'],
                'detalle': self.data_update['distribucion_list'][0]['detalle'],
                'monto': new_monto,
                'data': {'action': 'add'},
            }
        )
        self.client.put(
            f'/api/factura-distribuida/{self.data_update.get("factura_distribuida_id")}/',
            self.data_update,
            format='json',
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_factura_distribuida(self):
        """
        Valida que la factura quede marcada como distribuida si el monto distribuida es igual a la cant a distribuir.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.put(
            f'/api/factura-distribuida/{self.data_update.get("factura_distribuida_id")}/',
            self.data_update,
            format='json',
        )
        factura_distribuida_id = response.data.get('factura_distribuida_id')
        factura_distribuida = FacturaDistribuida.objects.get(pk=factura_distribuida_id)
        self.assertTrue(factura_distribuida.distribuida)

    def test_factura_no_distribuida(self):
        """
        Valida que la factura quede marcada como no distribuida si el monto distribuidp es menor a la cant a distribuir.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        self.data_update['distribucion_list'][0]['monto'] -= 1
        response = self.client.put(
            f'/api/factura-distribuida/{self.data_update.get("factura_distribuida_id")}/',
            self.data_update,
            format='json',
        )
        factura_distribuida_id = response.data.get('factura_distribuida_id')
        factura_distribuida = FacturaDistribuida.objects.get(pk=factura_distribuida_id)
        self.assertFalse(factura_distribuida.distribuida)


class FacturaDistribuidaSendNotificationAPITestCase(BaseTestCase):
    """Test sobre el serializador que envía notificaciones."""

    def setUp(self):
        self.client = APIClient()

    def test_re_send_notification(self):
        """Test reenvío de notificaciones a proveedores."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        factura_distribuida_proveedor = FacturaDistribuidaProveedorFactory.create()
        data = {
            'proveedor_id': factura_distribuida_proveedor.proveedor.pk,
            'factura_distribuida_id': factura_distribuida_proveedor.factura_distribucion.pk,
        }
        self.client.post('/api/factura-distribuida/send-notification/', data, format='json')
        self.assertEqual(len(mail.outbox), 1)
