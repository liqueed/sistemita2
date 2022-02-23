"""Factura imputada de clientes API test."""

from decimal import Decimal

# Django
from django.core.management import call_command
from rest_framework.test import APIClient

from sistemita.core.constants import ZERO_DECIMAL
from sistemita.core.models import Factura

# Sistemita
from sistemita.core.tests.factories import (
    FacturaClienteFactory,
    FacturaImputadaClienteFactory,
    FacturaImputadaClienteFactoryData,
)
from sistemita.utils.tests import (
    BaseTestCase,
    prevent_request_warnings,
    rand_range,
)


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('permissions_translation', verbosity=0)
    call_command('add_permissions', verbosity=0)


class FacturaImputadaClienteListViewAPITestCase(BaseTestCase):
    """Tests sobre la API de clientes."""

    def setUp(self):
        self.client = APIClient()

    def test_list_with_superuser(self):
        """Verifica que el usuario admin pueda listar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/api/factura-imputada/')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_list_with_anonymous(self):
        """Verifica que el usuario sin acceso no pueda listar."""
        request = self.client.get('/api/factura-imputada/')
        self.assertEqual(request.status_code, 403)

    def test_list_length(self):
        """Verifica que devuelva un listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        limit = rand_range(1, 10)
        FacturaImputadaClienteFactory.create_batch(limit)
        request = self.client.get('/api/factura-imputada/')
        self.assertEqual(len(request.json()), limit)

    def test_list_empty(self):
        """Verifica que devuelva un listado vacío."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        request = self.client.get('/api/factura-imputada/')
        self.assertEqual(len(request.json()), 0)


class FacturaImputadaClienteCreateViewAPITestCase(BaseTestCase):
    """Tests sobre la vista de crear."""

    def setUp(self):
        self.client = APIClient()
        self.data_create = FacturaImputadaClienteFactoryData().create()

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        self.assertEqual(response.status_code, 201)

    def test_add_with_user_authenticated(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        self.assertEqual(response.status_code, 201)

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear."""
        response = self.client.get('/cliente/agregar/')
        self.assertEqual(response.status_code, 302)

    @prevent_request_warnings
    def test_validate_id_cliente(self):
        """Valida que el cliente exista."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data['cliente_id'] = self.data_create.get('cliente_id') + 1
        response = self.client.post('/api/factura-imputada/', data, format='json')
        self.assertHasErrorDetail(response.data.get('cliente_id'), 'El cliente no existe.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_facturas_not_exists(self):
        """Valida la existencia de las facturas.."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data.get('facturas_list')[0]['factura'] = 0
        response = self.client.post('/api/factura-imputada/', data, format='json')
        self.assertHasErrorDetail(response.data.get('facturas_list'), 'La factura no existe.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_same_moneda(self):
        """Valida que las notas de creditos y facturas sean de la misma moneda."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        for row in data.get('facturas_list'):
            factura = Factura.objects.filter(pk=row.get('factura')).first()
            new_moneda = 'P' if factura.moneda == 'D' else 'D'
            Factura.objects.filter(pk=factura.pk).update(moneda=new_moneda)
            break
        response = self.client.post('/api/factura-imputada/', data, format='json')
        self.assertHasErrorDetail(response.data.get('facturas_list'), 'Las facturas deben ser de la misma monedas.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_facturas_not_repeat(self):
        """Valida que las facturas no estén repetidos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        repeat = data.get('facturas_list')[0]
        data.get('facturas_list').append(repeat)
        response = self.client.post('/api/factura-imputada/', data, format='json')
        self.assertHasErrorDetail(response.data.get('facturas_list'), 'Hay facturas repetidas.')
        self.assertEqual(response.status_code, 400)

    @prevent_request_warnings
    def test_validate_id_nota_de_credito(self):
        """Valida la existencia de las factura nota de credito.."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data['nota_de_credito_id'] = 0
        response = self.client.post('/api/factura-imputada/', data, format='json')
        self.assertHasErrorDetail(response.data.get('nota_de_credito_id'), 'La factura no existe.')
        self.assertEqual(response.status_code, 400)

    def test_validate_monto_facturas(self):
        """Valida el monto de las facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        amount = 0
        for row in self.data_create.get('facturas_list'):
            amount += Factura.objects.filter(pk=row.get('factura')).first().total
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        self.assertEqual(response.data.get('monto_facturas'), str(amount))

    def test_validate_type_nota_de_credito(self):
        """Valida que el tipo de factura de la nota de credito."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        nota_de_credito_id = response.data.get('nota_de_credito')['id']
        nota_de_credito = Factura.objects.get(pk=nota_de_credito_id)
        self.assertEqual(nota_de_credito.tipo, 'NC')

    def test_validate_monto_nota_de_credito(self):
        """Valida el monto de la nota de credito."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        self.assertEqual(response.data.get('monto_nota_de_credito'), str(nota_de_credito.total))

    def test_validate_total_facturas(self):
        """Valida el monto total de las facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        amount = 0
        for row in self.data_create.get('facturas_list'):
            amount += Factura.objects.filter(pk=row.get('factura')).first().total
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        total_factura = max(amount - nota_de_credito.total, ZERO_DECIMAL)
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        self.assertEqual(response.data.get('total_factura'), str(total_factura))

    def test_validate_total_factura_gte_zero(self):
        """Valida que el total de la factura sea cero"""
        self.create_user()
        self.client.login(username='user', password='user12345')
        amount = 0
        for row in self.data_create.get('facturas_list'):
            amount += Factura.objects.filter(pk=row.get('factura')).first().total
        Factura.objects.filter(pk=self.data_create.get('nota_de_credito_id')).update(total=amount)
        self.data_create['total_factura'] = 0
        self.data_create['monto_nota_de_credito'] = amount
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        self.assertEqual(response.data.get('total_factura'), '0.00')

    def test_validate_facturas_cobradas(self):
        """
        Valida que el monto de la nota de credito sea seteada como cobrada el monto de facturas
        es mayor o igual que el total de la nota de credito.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        amount = 0
        for row in self.data_create.get('facturas_list'):
            amount += Factura.objects.filter(pk=row.get('factura')).first().total
        self.client.post('/api/factura-imputada/', self.data_create, format='json')
        nota_de_credito.refresh_from_db()
        self.assertEqual(nota_de_credito.cobrado, nota_de_credito.total <= amount)

    def test_validate_nota_de_credito_total(self):
        """Valida el monto descontado a la nota de credito sobre el monto total de facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        amount = 0
        for row in self.data_create.get('facturas_list'):
            amount += Factura.objects.filter(pk=row.get('factura')).first().total
        amount_nota_de_credito = max(nota_de_credito.total - amount, 0)
        self.client.post('/api/factura-imputada/', self.data_create, format='json')
        nota_de_credito.refresh_from_db()
        self.assertEqual(nota_de_credito.total, amount_nota_de_credito)

    def test_validate_facturas_apply_nota_credito_on_facturas(self):
        """Valida el total de facturas luego de descontar la nota de credito."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        amount_nota_de_credito = nota_de_credito.total
        amounts = []
        for row in self.data_create.get('facturas_list'):
            if amount_nota_de_credito == 0:
                break
            factura = Factura.objects.get(pk=row.get('factura'))
            if amount_nota_de_credito == factura.total:
                amount_nota_de_credito -= factura.total
                amounts.append(
                    {'id': factura.pk, 'cobrado': True, 'monto_imputado': amount_nota_de_credito, 'total': ZERO_DECIMAL}
                )
            elif amount_nota_de_credito > factura.total:
                amount_nota_de_credito -= factura.total
                amounts.append(
                    {
                        'id': factura.pk,
                        'cobrado': True,
                        'monto_imputado': factura.total,
                        'total': max(factura.total - amount_nota_de_credito, ZERO_DECIMAL),
                    }
                )
            elif amount_nota_de_credito < factura.total:
                factura_total = factura.total - amount_nota_de_credito
                amounts.append(
                    {
                        'id': factura.pk,
                        'cobrado': False,
                        'monto_imputado': amount_nota_de_credito,
                        'total': factura_total,
                    }
                )
                amount_nota_de_credito = 0

        self.client.post('/api/factura-imputada/', self.data_create, format='json')
        nota_de_credito.refresh_from_db()
        results = False
        for row in amounts:
            results = Factura.objects.filter(
                pk=row.get('id'),
                cobrado=row.get('cobrado'),
                monto_imputado=row.get('monto_imputado'),
                total=row.get('total'),
            ).exists()
        self.assertTrue(results)


class FacturaImputadaClienteUpdateViewAPITestCase(BaseTestCase):
    """Tests sobre la vista de actualizar."""

    def setUp(self):
        self.client = APIClient()
        facturas = []
        for _ in range(0, 2):
            factura = FacturaClienteFactory.create(tipo='A', cobrado=False)
            facturas.append(factura)
        self.instance = FacturaImputadaClienteFactory.create(facturas=facturas)

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede editar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        instance = self.instance
        factura = FacturaClienteFactory.create(tipo='A', cobrado=False, moneda=instance.moneda)
        monto_facturas = instance.monto_facturas + factura.total
        total_factura = Decimal(monto_facturas) - instance.nota_de_credito.total
        data = FacturaImputadaClienteFactoryData().update(instance, [], monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_add_with_user_authenticated(self):
        """Verifica que el usuario autenticado pueda editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        factura = FacturaClienteFactory.create(tipo='A', cobrado=False, moneda=instance.moneda)
        monto_facturas = instance.monto_facturas + factura.total
        total_factura = Decimal(monto_facturas) - instance.nota_de_credito.total
        data = FacturaImputadaClienteFactoryData().update(instance, [], monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear."""
        instance = self.instance
        factura = FacturaClienteFactory.create(tipo='A', cobrado=False, moneda=instance.moneda)
        monto_facturas = instance.monto_facturas + factura.total
        total_factura = Decimal(monto_facturas) - instance.nota_de_credito.total
        data = FacturaImputadaClienteFactoryData().update(instance, [], monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_add_factura_to_instance(self):
        """Valida los datos al agregar una factura a una instancia de factura imputada."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        amount_facturas = instance.facturas.count()
        factura = FacturaClienteFactory.create(tipo='A', cobrado=False, moneda=instance.moneda)
        facturas_list = [{'factura': factura.pk, 'action': 'add'}]
        monto_facturas = instance.monto_facturas + factura.total
        total_factura = Decimal(monto_facturas) - instance.nota_de_credito.total
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.facturas.count(), amount_facturas + 1)
