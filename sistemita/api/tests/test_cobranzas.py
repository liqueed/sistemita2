"""Cobranza de clientes API test."""

# Django
from django.core.management import call_command
from rest_framework.test import APIClient

# Sistemita
from sistemita.accounting.models import CobranzaFactura, CobranzaFacturaPago
from sistemita.accounting.tests.factories import (
    CobranzaFactory,
    CobranzaFactoryData,
)
from sistemita.core.models import Cliente, Factura
from sistemita.core.tests.factories import FacturaClienteFactory
from sistemita.expense.models import Fondo
from sistemita.expense.tests.factories import FondoFactory
from sistemita.utils.tests import (
    BaseTestCase,
    prevent_request_warnings,
    rand_range,
)


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class CobranzaListViewAPITestCase(BaseTestCase):
    """Tests sobre la API de cobranzas."""

    def setUp(self):
        self.client = APIClient()

    def test_list_with_superuser(self):
        """Verifica que el usuario admin pueda listar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/api/cobranza/')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_list_with_anonymous(self):
        """Verifica que el usuario sin acceso no pueda listar."""
        request = self.client.get('/api/cobranza/')
        self.assertEqual(request.status_code, 403)

    def test_list_length(self):
        """Verifica que devuelva un listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        limit = rand_range(1, 10)
        CobranzaFactory.create_batch(limit)
        response = self.client.get('/api/cobranza/')
        self.assertEqual(len(response.json()), limit)
        self.assertEqual(response.status_code, 200)

    def test_list_empty(self):
        """Verifica que devuelva un listado vacío."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/api/cobranza/')
        self.assertEqual(len(response.json()), 0)
        self.assertEqual(response.status_code, 200)


class CobranzaCreateViewAPITestCase(BaseTestCase):
    """Tests sobre la vista de crear."""

    fixtures = [
        'fixtures/medio_pagos.json',
    ]

    def setUp(self):
        self.client = APIClient()
        self.data_create = CobranzaFactoryData().create()

    def test_validate_data(self):
        """Valida que si los datos son correcto agregue la instancia."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/cobranza/', self.data_create, format='json')
        self.assertEqual(response.status_code, 201)

    @prevent_request_warnings
    def test_validate_fields_required(self):
        """Valida los campos requeridos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/cobranza/', {}, format='json')
        required_fields = ['fecha', 'cliente', 'total', 'cobranza_facturas']
        self.assertHasProps(response.data, required_fields)
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_facturas_required(self):
        """Valida que la cantidad de facturas enviadas estén completas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data['cobranza_facturas'][0]['factura'] = None  # Remuevo una factura
        response = self.client.post('/api/cobranza/', data, format='json')
        self.assertHasErrorDetail(response.data.get('cobranza_facturas')[0]['factura'], 'Este campo no puede ser nulo.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_pagos_required(self):
        """Valida que la cantidad de pagos enviados estén completos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data['cobranza_facturas'][0]['cobranza_factura_pagos'][0]['metodo'] = None  # Remuevo un metodo
        response = self.client.post('/api/cobranza/', data, format='json')
        self.assertHasErrorDetail(
            response.data.get('cobranza_facturas')[0]['cobranza_factura_pagos'][0]['metodo'],
            'Este campo no puede ser nulo.',
        )
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_cliente(self):
        """Valida que el cliente exista."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data.update(
            {
                'cliente': {
                    'razon_social': 'Test S.R.L',
                    'cuit': 20111111118,
                    'correo': 'test@test.io',
                    'telefono': 1343454,
                }
            }
        )
        response = self.client.post('/api/cobranza/', data, format='json')
        self.assertHasErrorDetail(response.data.get('cliente'), 'El cliente no existe.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_moneda(self):
        """Valida que las facturas asociadas sean de la misma moneda."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        moneda = 'P' if data.get('moneda') == 'D' else 'D'
        cliente = Cliente.objects.get(cuit=data.get('cliente')['cuit'])
        factura = FacturaClienteFactory(cliente=cliente, tipo='A', moneda=moneda)
        data.get('cobranza_facturas').append(
            {
                'factura': factura.pk,
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'cobranza_factura_pagos': [{'metodo': 1, 'monto': 28.97}],
            }
        )
        response = self.client.post('/api/cobranza/', data, format='json')
        self.assertHasErrorDetail(response.data.get('cobranza_facturas'), 'Las facturas deben ser de la misma monedas.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_factura_repeat(self):
        """Valida que las facturas no estén repetidas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data.get('cobranza_facturas').append(
            {
                'factura': data.get('cobranza_facturas')[0]['factura'],
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'cobranza_factura_pagos': [{'metodo': 1, 'monto': 28.97}],
            }
        )
        response = self.client.post('/api/cobranza/', data, format='json')
        self.assertHasErrorDetail(response.data.get('cobranza_facturas'), 'Hay facturas repetidas.')
        self.assertEqual(response.status_code, 400)

    def test_validate_total(self):
        """Valida el total de la cobranza."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        total = 0
        for item in self.data_create.get('cobranza_facturas'):
            total += Factura.objects.get(pk=item.get('factura')).total
        response = self.client.post('/api/cobranza/', self.data_create, format='json')
        self.assertEqual(response.data.get('total'), str(total))
        self.assertEqual(response.status_code, 201)

    def test_create_cobranza_factura(self):
        """Valida que las se hayan creado las relación de facturas asociadas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        facturas_pk = []
        for factura in self.data_create.get('cobranza_facturas'):
            facturas_pk.append(factura.get('factura'))
        response = self.client.post('/api/cobranza/', self.data_create, format='json')
        cobranza_pk = response.data.get('id')
        results = 0
        for pk in facturas_pk:
            results += CobranzaFactura.objects.filter(cobranza__pk=cobranza_pk, factura__pk=pk).exists()
        self.assertEqual(len(facturas_pk), results)
        self.assertEqual(response.status_code, 201)

    def test_create_pagos(self):
        """Valida que se haya creado N pagos por N facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        pagos = []
        for factura in self.data_create.get('cobranza_facturas'):
            pagos.append(factura.get('cobranza_factura_pagos'))
        response = self.client.post('/api/cobranza/', self.data_create, format='json')
        cobranza_pk = response.data.get('id')
        results = 0
        for item in pagos:
            results += CobranzaFacturaPago.objects.filter(
                cobranza_factura__cobranza__pk=cobranza_pk, metodo=item[0]['metodo'], monto=item[0]['monto']
            ).exists()
        self.assertEqual(len(pagos), results)
        self.assertEqual(response.status_code, 201)

    def test_facturas_cobradas(self):
        """Valida que las facturas asocidas pasen a estar cobradas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        facturas_pk = []
        for factura in self.data_create.get('cobranza_facturas'):
            facturas_pk.append(factura.get('factura'))
        response = self.client.post('/api/cobranza/', self.data_create, format='json')
        results = 0
        for pk in facturas_pk:
            results += Factura.objects.get(pk=pk).cobrado
        self.assertEqual(results, len(facturas_pk))
        self.assertEqual(response.status_code, 201)

    def test_fondos_disponibles(self):
        """Valida que los fondos de las facturas asociadas pasen a estar disponibles."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        facturas_pk = []
        for factura in self.data_create.get('cobranza_facturas'):
            pk = factura.get('factura')
            factura = Factura.objects.get(pk=pk)
            FondoFactory.create(factura=factura, disponible=False)
            facturas_pk.append(pk)
        response = self.client.post('/api/cobranza/', self.data_create, format='json')
        results = 0
        for pk in facturas_pk:
            results += Fondo.objects.get(factura__pk=pk).disponible
        self.assertEqual(results, len(facturas_pk))
        self.assertEqual(response.status_code, 201)


class CobranzaUpdateViewAPITestCase(BaseTestCase):
    """Tests sobre la vista de actualizar."""

    fixtures = [
        'fixtures/medio_pagos.json',
    ]

    def setUp(self):
        self.client = APIClient()
        self.data_update = CobranzaFactoryData().update()

    def test_validate_data(self):
        """Valida que si los datos son correcto agregue la instancia."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', self.data_update, format='json')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_validate_fields_required(self):
        """Valida los campos requeridos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', {}, format='json')
        required_fields = ['fecha', 'cliente', 'total', 'cobranza_facturas']
        self.assertHasProps(response.data, required_fields)
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_facturas_required(self):
        """Valida que la cantidad de facturas enviadas estén completas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        data['cobranza_facturas'][0]['factura'] = None  # Remuevo una factura
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_pagos_required(self):
        """Valida que la cantidad de pagos enviados estén completos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        data['cobranza_facturas'][0]['cobranza_factura_pagos'][0]['metodo'] = None  # Remuevo un metodo
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        self.assertHasErrorDetail(
            response.data.get('cobranza_facturas')[0]['cobranza_factura_pagos'][0]['metodo'],
            'Este campo no puede ser nulo.',
        )
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_cliente(self):
        """Valida que el cliente exista."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        data.update(
            {
                'cliente': {
                    'razon_social': 'Test S.R.L',
                    'cuit': 20111111118,
                    'correo': 'test@test.io',
                    'telefono': 1343454,
                }
            }
        )
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        self.assertHasErrorDetail(response.data.get('cliente'), 'El cliente no existe.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_moneda(self):
        """Valida que las facturas asociadas sean de la misma moneda. Agrego una nueva factura"""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        moneda = 'P' if data.get('moneda') == 'D' else 'D'
        cliente = Cliente.objects.get(cuit=data.get('cliente')['cuit'])
        factura = FacturaClienteFactory(cliente=cliente, tipo='A', moneda=moneda)
        data.get('cobranza_facturas').append(
            {
                'data': {'id': factura.pk, 'action': 'add'},
                'factura': factura.pk,
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'cobranza_factura_pagos': [{'metodo': 1, 'monto': 28.97}],
            }
        )
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        self.assertHasErrorDetail(response.data.get('cobranza_facturas'), 'Las facturas deben ser de la misma monedas.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_factura_repeat(self):
        """Valida que las facturas no estén repetidas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        data.get('cobranza_facturas').append(
            {
                'factura': data.get('cobranza_facturas')[0]['factura'],
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'cobranza_factura_pagos': [{'metodo': 1, 'monto': 28.97}],
            }
        )
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        self.assertHasErrorDetail(response.data.get('cobranza_facturas'), 'Hay facturas repetidas.')
        self.assertEqual(response.status_code, 400)

    def test_validate_total(self):
        """
        Valida el total de la cobranza. Edito una factura.
        En lo requerimientos el total es un campo editable por lo cual no se valida.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        cliente = Cliente.objects.get(cuit=data.get('cliente')['cuit'])

        total = 0
        factura = FacturaClienteFactory.create(cliente=cliente, tipo='A', moneda=data.get('moneda'))
        for item in data.get('cobranza_facturas'):
            total += Factura.objects.get(pk=item.get('factura')).total

        data['total'] = total
        data['cobranza_facturas'][0] = {
            'data': {'id': data.get('cobranza_facturas')[0]['data']['id'], 'action': 'update'},
            'factura': factura.pk,
            'ganancias': data.get('cobranza_facturas')[0]['ganancias'],
            'ingresos_brutos': data.get('cobranza_facturas')[0]['ingresos_brutos'],
            'iva': data.get('cobranza_facturas')[0]['iva'],
            'suss': data.get('cobranza_facturas')[0]['suss'],
            'cobranza_factura_pagos': [
                {
                    'data': data.get('cobranza_facturas')[0]['cobranza_factura_pagos'][0]['data'],
                    'metodo': data.get('cobranza_facturas')[0]['cobranza_factura_pagos'][0]['metodo'],
                    'monto': data.get('cobranza_facturas')[0]['cobranza_factura_pagos'][0]['monto'],
                }
            ],
        }
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        self.assertEqual(response.data.get('total'), str(total))
        self.assertEqual(response.status_code, 200)

    def test_update_add_facturas(self):
        """Valida que se agregue una nueva factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        cliente = Cliente.objects.get(cuit=data.get('cliente')['cuit'])
        factura = FacturaClienteFactory(cliente=cliente, tipo='A', moneda=data.get('moneda'))
        data.get('cobranza_facturas').append(
            {
                'data': {'id': data['id'], 'action': 'add'},
                'factura': factura.pk,
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'cobranza_factura_pagos': [{'metodo': 2, 'monto': 50.00}],
            }
        )
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_update_replace_factura(self):
        """
        Valida que la factura reemplazada pasa a estar como no cobrada y el fondo como no disponible.
        La nueva factura asociada pasa a estar como cobrada y el fondo disponible.
        La nueva factura pasa a estar asociada la cobranza.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        cliente = Cliente.objects.get(cuit=data.get('cliente')['cuit'])
        factura = FacturaClienteFactory(cliente=cliente, tipo='A', moneda=data.get('moneda'), cobrado=False)
        FondoFactory.create(factura=factura, disponible=False)
        data.get('cobranza_facturas').append(
            {
                'data': {'id': data['id'], 'action': 'add'},
                'factura': factura.pk,
                'ganancias': 0,
                'ingresos_brutos': 0,
                'iva': 0,
                'suss': 0,
                'cobranza_factura_pagos': [{'metodo': 2, 'monto': 50.00}],
            }
        )
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        factura.refresh_from_db()
        self.assertTrue(factura.cobrado)
        self.assertTrue(factura.factura_fondo.all().first().disponible)  # La factura solo tiene un fondo
        self.assertEqual(response.status_code, 200)

    def test_update_delete_factura(self):
        """
        Valida que la factura eliminada pasa a estar como no cobrada y el fondo como no disponible.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        factura_delete = data.get('cobranza_facturas')[0]['factura']
        factura = Factura.objects.get(pk=factura_delete)
        FondoFactory.create(factura=factura, disponible=True)
        data['cobranza_facturas'][0] = {
            'data': {'id': data.get('cobranza_facturas')[0]['data']['id'], 'action': 'delete'},
            'factura': factura_delete,
            'ganancias': data.get('cobranza_facturas')[0]['ganancias'],
            'ingresos_brutos': data.get('cobranza_facturas')[0]['ingresos_brutos'],
            'iva': data.get('cobranza_facturas')[0]['iva'],
            'suss': data.get('cobranza_facturas')[0]['suss'],
            'cobranza_factura_pagos': [
                {
                    'data': data.get('cobranza_facturas')[0]['cobranza_factura_pagos'][0]['data'],
                    'metodo': data.get('cobranza_facturas')[0]['cobranza_factura_pagos'][0]['metodo'],
                    'monto': data.get('cobranza_facturas')[0]['cobranza_factura_pagos'][0]['monto'],
                }
            ],
        }
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        factura = Factura.objects.get(pk=factura_delete)
        factura.refresh_from_db()
        self.assertFalse(factura.cobrado)
        self.assertFalse(factura.factura_fondo.all().first().disponible)  # La factura solo tiene un fondo
        self.assertEqual(response.status_code, 200)

    def test_update_pago_add(self):
        """Valida el agregar un metodo de pago."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        data['cobranza_facturas'][0]['cobranza_factura_pagos'].append(
            {
                'data': {'action': 'add'},
                'metodo': 2,
                'monto': 100,
            }
        )
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_update_pago_update(self):
        """Valida el editar un metodo de pago."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        cobranza_pago_pk = data['cobranza_facturas'][0]['cobranza_factura_pagos'][0]['data']['id']
        metodo = 2
        monto = 100
        data['cobranza_facturas'][0]['cobranza_factura_pagos'][0] = {
            'data': {'id': cobranza_pago_pk, 'action': 'update'},
            'metodo': metodo,
            'monto': monto,
        }
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        self.assertTrue(
            CobranzaFacturaPago.objects.filter(pk=cobranza_pago_pk, metodo__pk=metodo, monto=monto).exists()
        )
        self.assertEqual(response.status_code, 200)

    def test_update_pago_delete(self):
        """Valida el eliminar un metodo de pago."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_update
        cobranza_pago_pk = data['cobranza_facturas'][0]['cobranza_factura_pagos'][0]['data']['id']
        data['cobranza_facturas'][0]['cobranza_factura_pagos'][0] = {
            'data': {'id': cobranza_pago_pk, 'action': 'delete'},
            'metodo': data['cobranza_facturas'][0]['cobranza_factura_pagos'][0]['metodo'],
            'monto': data['cobranza_facturas'][0]['cobranza_factura_pagos'][0]['monto'],
        }
        response = self.client.put(f'/api/cobranza/{self.data_update.get("id")}/', data, format='json')
        self.assertFalse(CobranzaFacturaPago.objects.filter(pk=cobranza_pago_pk).exists())
        self.assertEqual(response.status_code, 200)
