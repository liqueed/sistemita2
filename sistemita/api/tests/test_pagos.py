"""Pago de clientes API test."""

# Django
from django.core.management import call_command
from rest_framework.test import APIClient

# Sistemita
from sistemita.accounting.models import PagoFactura, PagoFacturaPago
from sistemita.accounting.tests.factories import PagoFactory, PagoFactoryData
from sistemita.core.models import FacturaProveedor, Proveedor
from sistemita.core.tests.factories import FacturaProveedorFactory
from sistemita.utils.tests import (
    BaseTestCase,
    prevent_request_warnings,
    rand_range,
)


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class PagoListViewAPITestCase(BaseTestCase):
    """Tests sobre la API de pagos."""

    def setUp(self):
        self.client = APIClient()

    def test_list_with_superuser(self):
        """Verifica que el usuario admin pueda listar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/api/pago/')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_list_with_anonymous(self):
        """Verifica que el usuario sin acceso no pueda listar."""
        request = self.client.get('/api/pago/')
        self.assertEqual(request.status_code, 403)

    def test_list_length(self):
        """Verifica que devuelva un listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        limit = rand_range(1, 10)
        PagoFactory.create_batch(limit)
        response = self.client.get('/api/pago/')
        self.assertEqual(len(response.json()), limit)
        self.assertEqual(response.status_code, 200)

    def test_list_empty(self):
        """Verifica que devuelva un listado vacío."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/api/pago/')
        self.assertEqual(len(response.json()), 0)
        self.assertEqual(response.status_code, 200)


class PagoCreateViewAPITestCase(BaseTestCase):
    """Tests sobre la vista de crear."""

    fixtures = [
        'fixtures/medio_pagos.json',
    ]

    def setUp(self):
        self.client = APIClient()
        self.data_create = PagoFactoryData().create()

    def test_validate_data(self):
        """Valida que si los datos son correcto agregue la instancia."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/pago/', self.data_create, format='json')
        self.assertEqual(response.status_code, 201)

    @prevent_request_warnings
    def test_validate_fields_required(self):
        """Valida los campos requeridos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/pago/', {}, format='json')
        required_fields = ['fecha', 'proveedor', 'total', 'pago_facturas']
        self.assertHasProps(response.data, required_fields)
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_facturas_required(self):
        """Valida que la cantidad de facturas enviadas estén completas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data['pago_facturas'][0]['factura'] = None  # Remuevo una factura
        response = self.client.post('/api/pago/', data, format='json')
        self.assertHasErrorDetail(response.data.get('pago_facturas')[0]['factura'], 'Este campo no puede ser nulo.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_pagos_required(self):
        """Valida que la cantidad de pagos enviados estén completos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data['pago_facturas'][0]['pago_factura_pagos'][0]['metodo'] = None  # Remuevo un metodo
        response = self.client.post('/api/pago/', data, format='json')
        self.assertHasErrorDetail(
            response.data.get('pago_facturas')[0]['pago_factura_pagos'][0]['metodo'],
            'Este campo no puede ser nulo.',
        )
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_proveedor(self):
        """Valida que el proveedor exista."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data.update(
            {
                'proveedor': 20111111118
            }
        )
        response = self.client.post('/api/pago/', data, format='json')
        self.assertHasErrorDetail(response.data.get('proveedor'), 'El proveedor no existe.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_moneda(self):
        """Valida que las facturas asociadas sean de la misma moneda."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        moneda = 'P' if data.get('moneda') == 'D' else 'D'
        proveedor = Proveedor.objects.get(cuit=data.get('proveedor'))
        factura = FacturaProveedorFactory(proveedor=proveedor, tipo='A', moneda=moneda)
        data.get('pago_facturas').append(
            {
                'factura': factura.pk,
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'pago_factura_pagos': [{'metodo': 1, 'monto': 28.97}],
            }
        )
        response = self.client.post('/api/pago/', data, format='json')
        self.assertHasErrorDetail(response.data.get('pago_facturas'), 'Las facturas deben ser de la misma monedas.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_factura_repeat(self):
        """Valida que las facturas no estén repetidas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data.get('pago_facturas').append(
            {
                'factura': data.get('pago_facturas')[0]['factura'],
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'pago_factura_pagos': [{'metodo': 1, 'monto': 28.97}],
            }
        )
        response = self.client.post('/api/pago/', data, format='json')
        self.assertHasErrorDetail(response.data.get('pago_facturas'), 'Hay facturas repetidas.')
        self.assertEqual(response.status_code, 400)

    def test_validate_total(self):
        """Valida el total de la pago."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        total = 0
        for item in self.data_create.get('pago_facturas'):
            total += FacturaProveedor.objects.get(pk=item.get('factura')).total
        response = self.client.post('/api/pago/', self.data_create, format='json')
        self.assertEqual(response.data.get('total'), str(total))
        self.assertEqual(response.status_code, 201)

    def test_create_pago_factura(self):
        """Valida que las se hayan creado las relación de facturas asociadas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        facturas_pk = []
        for factura in self.data_create.get('pago_facturas'):
            facturas_pk.append(factura.get('factura'))
        response = self.client.post('/api/pago/', self.data_create, format='json')
        pago_pk = response.data.get('id')
        results = 0
        for pk in facturas_pk:
            results += PagoFactura.objects.filter(pago__pk=pago_pk, factura__pk=pk).exists()
        self.assertEqual(len(facturas_pk), results)
        self.assertEqual(response.status_code, 201)

    def test_create_pagos(self):
        """Valida que se haya creado N pagos por N facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        pagos = []
        for factura in self.data_create.get('pago_facturas'):
            pagos.append(factura.get('pago_factura_pagos'))
        response = self.client.post('/api/pago/', self.data_create, format='json')
        pago_pk = response.data.get('id')
        results = 0
        for item in pagos:
            results += PagoFacturaPago.objects.filter(
                pago_factura__pago__pk=pago_pk, metodo=item[0]['metodo'], monto=item[0]['monto']
            ).exists()
        self.assertEqual(len(pagos), results)
        self.assertEqual(response.status_code, 201)

    def test_facturas_cobradas(self):
        """Valida que las facturas asocidas pasen a estar cobradas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        facturas_pk = []
        for factura in self.data_create.get('pago_facturas'):
            facturas_pk.append(factura.get('factura'))
        response = self.client.post('/api/pago/', self.data_create, format='json')
        results = 0
        for pk in facturas_pk:
            results += FacturaProveedor.objects.get(pk=pk).cobrado
        self.assertEqual(results, len(facturas_pk))
        self.assertEqual(response.status_code, 201)


class PagoUpdateViewAPITestCase(BaseTestCase):
    """Tests sobre la vista de actualizar."""

    fixtures = [
        'fixtures/medio_pagos.json',
    ]

    def setUp(self):
        self.client = APIClient()
        self.data_update = PagoFactoryData().update()

    def test_validate_data(self):
        """Valida que si los datos son correcto agregue la instancia."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', self.data_update, format='json')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_validate_fields_required(self):
        """Valida los campos requeridos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', {}, format='json')
        required_fields = ['fecha', 'proveedor', 'total', 'pago_facturas']
        self.assertHasProps(response.data, required_fields)
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_facturas_required(self):
        """Valida que la cantidad de facturas enviadas estén completas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        data['pago_facturas'][0]['factura'] = None  # Remuevo una factura
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_pagos_required(self):
        """Valida que la cantidad de pagos enviados estén completos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        data['pago_facturas'][0]['pago_factura_pagos'][0]['metodo'] = None  # Remuevo un metodo
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        self.assertHasErrorDetail(
            response.data.get('pago_facturas')[0]['pago_factura_pagos'][0]['metodo'],
            'Este campo no puede ser nulo.',
        )
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_proveedor(self):
        """Valida que el proveedor exista."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        data.update(
            {
                'proveedor': 20111111118
            }
        )
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        self.assertHasErrorDetail(response.data.get('proveedor'), 'El proveedor no existe.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_moneda(self):
        """Valida que las facturas asociadas sean de la misma moneda. Agrego una nueva factura"""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        moneda = 'P' if data.get('moneda') == 'D' else 'D'
        proveedor = Proveedor.objects.get(cuit=data.get('proveedor'))
        factura = FacturaProveedorFactory(proveedor=proveedor, tipo='A', moneda=moneda)
        data.get('pago_facturas').append(
            {
                'data': {'id': factura.pk, 'action': 'add'},
                'factura': factura.pk,
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'pago_factura_pagos': [{'metodo': 1, 'monto': 28.97}],
            }
        )
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        self.assertHasErrorDetail(response.data.get('pago_facturas'), 'Las facturas deben ser de la misma monedas.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_factura_repeat(self):
        """Valida que las facturas no estén repetidas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        data.get('pago_facturas').append(
            {
                'factura': data.get('pago_facturas')[0]['factura'],
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'pago_factura_pagos': [{'metodo': 1, 'monto': 28.97}],
            }
        )
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        self.assertHasErrorDetail(response.data.get('pago_facturas'), 'Hay facturas repetidas.')
        self.assertEqual(response.status_code, 400)

    def test_validate_total(self):
        """
        Valida el total de la pago. Edito una factura.
        En lo requerimientos el total es un campo editable por lo cual no se valida.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        proveedor = Proveedor.objects.get(cuit=data.get('proveedor'))

        total = 0
        factura = FacturaProveedorFactory.create(proveedor=proveedor, tipo='A', moneda=data.get('moneda'))
        for item in data.get('pago_facturas'):
            total += FacturaProveedor.objects.get(pk=item.get('factura')).total

        data['total'] = total
        data['pago_facturas'][0] = {
            'data': {'id': data.get('pago_facturas')[0]['data']['id'], 'action': 'update'},
            'factura': factura.pk,
            'ganancias': data.get('pago_facturas')[0]['ganancias'],
            'ingresos_brutos': data.get('pago_facturas')[0]['ingresos_brutos'],
            'iva': data.get('pago_facturas')[0]['iva'],
            'suss': data.get('pago_facturas')[0]['suss'],
            'pago_factura_pagos': [
                {
                    'data': data.get('pago_facturas')[0]['pago_factura_pagos'][0]['data'],
                    'metodo': data.get('pago_facturas')[0]['pago_factura_pagos'][0]['metodo'],
                    'monto': data.get('pago_facturas')[0]['pago_factura_pagos'][0]['monto'],
                }
            ],
        }
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        self.assertEqual(response.data.get('total'), str(total))
        self.assertEqual(response.status_code, 200)

    def test_update_add_facturas(self):
        """Valida que se agregue una nueva factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        proveedor = Proveedor.objects.get(cuit=data.get('proveedor'))
        factura = FacturaProveedorFactory(proveedor=proveedor, tipo='A', moneda=data.get('moneda'))
        data.get('pago_facturas').append(
            {
                'data': {'id': data['id'], 'action': 'add'},
                'factura': factura.pk,
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'pago_factura_pagos': [{'metodo': 2, 'monto': 50.00}],
            }
        )
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_update_replace_factura(self):
        """
        Valida que la factura reemplazada pasa a estar como no cobrada y el fondo como no disponible.
        La nueva factura asociada pasa a estar como cobrada y el fondo disponible.
        La nueva factura pasa a estar asociada la pago.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        proveedor = Proveedor.objects.get(cuit=data.get('proveedor'))
        factura = FacturaProveedorFactory(proveedor=proveedor, tipo='A', moneda=data.get('moneda'), cobrado=False)
        data.get('pago_facturas').append(
            {
                'data': {'id': data['id'], 'action': 'add'},
                'factura': factura.pk,
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'pago_factura_pagos': [{'metodo': 2, 'monto': 50.00}],
            }
        )
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        factura.refresh_from_db()
        self.assertTrue(factura.cobrado)
        self.assertEqual(response.status_code, 200)

    def test_update_delete_factura(self):
        """
        Valida que la factura eliminada pasa a estar como no cobrada y el fondo como no disponible.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        factura_delete = data.get('pago_facturas')[0]['factura']
        factura = FacturaProveedor.objects.get(pk=factura_delete)
        data['pago_facturas'][0] = {
            'data': {'id': data.get('pago_facturas')[0]['data']['id'], 'action': 'delete'},
            'factura': factura_delete,
            'ganancias': data.get('pago_facturas')[0]['ganancias'],
            'ingresos_brutos': data.get('pago_facturas')[0]['ingresos_brutos'],
            'iva': data.get('pago_facturas')[0]['iva'],
            'suss': data.get('pago_facturas')[0]['suss'],
            'pago_factura_pagos': [
                {
                    'data': data.get('pago_facturas')[0]['pago_factura_pagos'][0]['data'],
                    'metodo': data.get('pago_facturas')[0]['pago_factura_pagos'][0]['metodo'],
                    'monto': data.get('pago_facturas')[0]['pago_factura_pagos'][0]['monto'],
                }
            ],
        }
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        factura = FacturaProveedor.objects.get(pk=factura_delete)
        factura.refresh_from_db()
        self.assertFalse(factura.cobrado)
        self.assertEqual(response.status_code, 200)

    def test_update_pago_add(self):
        """Valida el agregar un metodo de pago."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        data['pago_facturas'][0]['pago_factura_pagos'].append(
            {
                'data': {'action': 'add'},
                'metodo': 2,
                'monto': 100,
            }
        )
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_update_pago_update(self):
        """Valida el editar un metodo de pago."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        pago_pago_pk = data['pago_facturas'][0]['pago_factura_pagos'][0]['data']['id']
        metodo = 2
        monto = 100
        data['pago_facturas'][0]['pago_factura_pagos'][0] = {
            'data': {'id': pago_pago_pk, 'action': 'update'},
            'metodo': metodo,
            'monto': monto,
        }
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        self.assertTrue(PagoFacturaPago.objects.filter(pk=pago_pago_pk, metodo__pk=metodo, monto=monto).exists())
        self.assertEqual(response.status_code, 200)

    def test_update_pago_delete(self):
        """Valida el eliminar un metodo de pago."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        pago_pago_pk = data['pago_facturas'][0]['pago_factura_pagos'][0]['data']['id']
        data['pago_facturas'][0]['pago_factura_pagos'][0] = {
            'data': {'id': pago_pago_pk, 'action': 'delete'},
            'metodo': data['pago_facturas'][0]['pago_factura_pagos'][0]['metodo'],
            'monto': data['pago_facturas'][0]['pago_factura_pagos'][0]['monto'],
        }
        response = self.client.put(f'/api/pago/{self.data_update.get("id")}/', data, format='json')
        self.assertFalse(PagoFacturaPago.objects.filter(pk=pago_pago_pk).exists())
        self.assertEqual(response.status_code, 200)
