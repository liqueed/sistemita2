"""Factura imputada de clientes API test."""

from decimal import Decimal

# Django
from django.core.management import call_command
from rest_framework.test import APIClient

# Sistemita
from sistemita.core.constants import ZERO_DECIMAL
from sistemita.core.models import Factura
from sistemita.core.tests.factories import (
    FacturaClienteFactory,
    FacturaImputadaClienteFactory,
    FacturaImputadaClienteFactoryData,
)
from sistemita.core.utils.commons import get_total_factura
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
        response = self.client.get('/api/factura-imputada/')
        self.assertEqual(len(response.json()), limit)
        self.assertEqual(response.status_code, 200)

    def test_list_empty(self):
        """Verifica que devuelva un listado vacío."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/api/factura-imputada/')
        self.assertEqual(len(response.json()), 0)
        self.assertEqual(response.status_code, 200)


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
            factura = Factura.objects.get(pk=row.get('factura'))
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
        monto_facturas = 0
        for row in self.data_create.get('facturas_list'):
            monto_facturas += Factura.objects.get(pk=row.get('factura')).total
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        self.assertEqual(Decimal(response.data.get('monto_facturas')), monto_facturas)
        self.assertEqual(response.status_code, 201)

    def test_validate_type_nota_de_credito(self):
        """Valida que el tipo de factura de la nota de credito."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        nota_de_credito_id = response.data.get('nota_de_credito').get('id')
        nota_de_credito = Factura.objects.get(pk=nota_de_credito_id)
        self.assertEqual(nota_de_credito.tipo, 'NC')
        self.assertEqual(response.status_code, 201)

    def test_validate_monto_nota_de_credito(self):
        """Valida el monto de la nota de credito."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        self.assertEqual(Decimal(response.data.get('monto_nota_de_credito')), nota_de_credito.total)
        self.assertEqual(response.status_code, 201)

    def test_validate_total_facturas(self):
        """Valida el monto total de las facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        monto_facturas = 0
        for row in self.data_create.get('facturas_list'):
            monto_facturas += Factura.objects.get(pk=row.get('factura')).total
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        total_factura = get_total_factura(monto_facturas, nota_de_credito.total_sin_imputar)
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        self.assertEqual(Decimal(response.data.get('total_factura')), total_factura)
        self.assertEqual(response.status_code, 201)

    def test_validate_total_factura_gte_zero(self):
        """Valida que el total de la factura sea cero"""
        self.create_user()
        self.client.login(username='user', password='user12345')
        monto_facturas = 0
        for row in self.data_create.get('facturas_list'):
            monto_facturas += Factura.objects.get(pk=row.get('factura')).total
        Factura.objects.filter(pk=self.data_create.get('nota_de_credito_id')).update(total=monto_facturas)
        self.data_create['total_factura'] = 0
        self.data_create['monto_nota_de_credito'] = monto_facturas
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        self.assertEqual(Decimal(response.data.get('total_factura')), ZERO_DECIMAL)
        self.assertEqual(response.status_code, 201)

    def test_validate_facturas_cobradas(self):
        """
        Valida que el monto de la nota de credito sea seteada como cobrada si el monto de facturas
        es mayor o igual que el total de la nota de credito.
        """
        self.create_user()
        self.client.login(username='user', password='user12345')
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        monto_facturas = 0
        for row in self.data_create.get('facturas_list'):
            monto_facturas += Factura.objects.filter(pk=row.get('factura')).first().total_sin_imputar
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        nota_de_credito.refresh_from_db()
        self.assertEqual(nota_de_credito.cobrado, nota_de_credito.total_sin_imputar <= monto_facturas)
        self.assertEqual(response.status_code, 201)

    def test_validate_total_factura(self):
        """Valida el monto descontado a la nota de credito sobre el monto total de facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        monto_facturas = 0
        for row in self.data_create.get('facturas_list'):
            monto_facturas += Factura.objects.filter(pk=row.get('factura')).first().total
        monto_nota_de_credito = max(nota_de_credito.total - monto_facturas, 0)
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        nota_de_credito.refresh_from_db()
        self.assertEqual(nota_de_credito.total, monto_nota_de_credito)
        self.assertEqual(response.status_code, 201)

    def test_validate_facturas_apply_nota_credito_on_facturas(self):
        """Valida el total de facturas luego de descontar la nota de credito."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        facturas = []
        total_nc = nota_de_credito.total
        for factura in self.data_create.get('facturas_list'):
            item = Factura.objects.get(pk=factura.get('factura'))
            factura_total = get_total_factura(item.total_sin_imputar, total_nc)
            factura_monto_imputado = item.total_sin_imputar if factura_total == 0 else total_nc
            total_nc -= item.total_sin_imputar if total_nc > item.total_sin_imputar else total_nc
            facturas.append(
                {
                    'id': item.pk,
                    'cobrado': not bool(factura_total),
                    'monto_imputado': factura_monto_imputado,
                    'total': factura_total,
                }
            )

        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        nota_de_credito.refresh_from_db()
        results = 0
        for row in facturas:
            results += Factura.objects.filter(
                pk=row.get('id'),
                cobrado=row.get('cobrado'),
                monto_imputado=row.get('monto_imputado'),
                total=row.get('total'),
            ).exists()
        self.assertEqual(results, len(facturas))
        self.assertEqual(response.status_code, 201)

    def test_validate_nota_de_credito(self):
        """Valida los datos de nota de credito luego de imputar facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        nota_de_credito = Factura.objects.get(pk=self.data_create.get('nota_de_credito_id'))
        total_nc = nota_de_credito.total
        for factura in self.data_create.get('facturas_list'):
            item = Factura.objects.get(pk=factura.get('factura'))
            total_nc -= item.total_sin_imputar if total_nc > item.total_sin_imputar else total_nc
        response = self.client.post('/api/factura-imputada/', self.data_create, format='json')
        nota_de_credito.refresh_from_db()
        self.assertEqual(nota_de_credito.total, total_nc)
        self.assertEqual(response.status_code, 201)


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
        facturas_list = []
        new_factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        for f in instance.facturas.all():
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append({'factura': new_factura.pk, 'action': 'add'})  # Agrega un nueva factura
        monto_facturas = instance.monto_facturas + new_factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        self.assertEqual(response.status_code, 200)

    def test_update_with_user_authenticated(self):
        """Verifica que el usuario autenticado pueda editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        new_factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        for f in instance.facturas.all():
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append({'factura': new_factura.pk, 'action': 'add'})  # Agrega un nueva factura
        monto_facturas = instance.monto_facturas + new_factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_update_with_user_anonymous(self):
        """Verifica que no pueda editar si no es un usuario autenticado."""
        instance = self.instance
        facturas_list = []
        new_factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        for f in instance.facturas.all():
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append({'factura': new_factura.pk, 'action': 'add'})  # Agrega una nueva factura
        monto_facturas = instance.monto_facturas + new_factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_update_add_factura(self):
        """Valida los datos al agregar una factura a una instancia de factura imputada."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        amount_facturas = instance.facturas.count()
        factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        for f in instance.facturas.all():
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append({'factura': factura.pk, 'action': 'add'})  # Agrega una nueva factura
        monto_facturas = instance.monto_facturas + factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.facturas.count(), amount_facturas + 1)
        self.assertEqual(response.status_code, 200)

    def test_update_add_factura_validate_monto_facturas(self):
        """Valida el monto de facturas al agrega un nueva factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        for f in instance.facturas.all():
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append({'factura': factura.pk, 'action': 'add'})  # Agrego una nueva factura
        monto_facturas = instance.monto_facturas + factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.monto_facturas, monto_facturas)
        self.assertEqual(response.status_code, 200)

    def test_update_add_factura_validate_monto_nota_de_credito(self):
        """Valida el monto de nota de credito al agregar una factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        monto_nota_de_credito = instance.monto_nota_de_credito
        factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        for f in instance.facturas.all():
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append({'factura': factura.pk, 'action': 'add'})  # Agrego una nueva factura
        monto_facturas = instance.monto_facturas + factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.monto_nota_de_credito, monto_nota_de_credito)
        self.assertEqual(response.status_code, 200)

    def test_update_add_factura_validate_total_factura(self):
        """Valida el total de factura al agregar una factura a una instancia de factura imputada."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        for f in instance.facturas.all():
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append({'factura': factura.pk, 'action': 'add'})  # Agrego una nueva factura
        monto_facturas = instance.monto_facturas + factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.total_factura, total_factura)
        self.assertEqual(response.status_code, 200)

    def test_update_add_factura_validate_facturas_montos_imputados(self):
        """Valida los montos imputados a las facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        facturas_validate = []
        total_nc = instance.nota_de_credito.total_sin_imputar
        new_factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        for factura in instance.facturas.order_by('facturas_imputacion').all():
            factura_total = get_total_factura(factura.total_sin_imputar, total_nc)
            factura_monto_imputado = factura.total_sin_imputar if factura_total == 0 else total_nc
            total_nc -= factura.total_sin_imputar if total_nc > factura.total_sin_imputar else total_nc
            facturas_validate.append({'id': factura.pk, 'monto_imputado': factura_monto_imputado})
            facturas_list.append(
                {'factura': factura.pk, 'action': '{"id": ' + str(factura.pk) + ', \"action\": "update"}'}
            )

        facturas_list.append({'factura': new_factura.pk, 'action': 'add'})  # Agrego una nueva factura

        factura_total = get_total_factura(new_factura.total, total_nc)
        factura_monto_imputado = new_factura.total if factura_total == 0 else total_nc
        facturas_validate.append({'id': new_factura.pk, 'monto_imputado': factura_monto_imputado})
        monto_facturas = instance.monto_facturas + new_factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)

        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        for factura in instance.facturas.all().order_by('facturas_imputacion'):
            self.assertEqual(
                factura.monto_imputado,
                [item for item in facturas_validate if item.get('id') == factura.pk][0].get('monto_imputado'),
            )
        self.assertEqual(response.status_code, 200)

    def test_update_add_factura_validate_nota_de_credito(self):
        """Valida los datos de la nota de credito luego de imputar facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        total_nc = instance.nota_de_credito.total_sin_imputar
        new_factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        for factura in instance.facturas.all():
            total_nc -= factura.total_sin_imputar if total_nc > factura.total_sin_imputar else total_nc
            facturas_list.append(
                {'factura': factura.pk, 'action': '{"id": ' + str(factura.pk) + ', \"action\": "update"}'}
            )

        facturas_list.append({'factura': new_factura.pk, 'action': 'add'})  # Agrego una nueva factura
        total_nc -= new_factura.total_sin_imputar if total_nc > new_factura.total_sin_imputar else total_nc
        monto_facturas = instance.monto_facturas + new_factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)

        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.nota_de_credito.total, total_nc)
        self.assertEqual(response.status_code, 200)

    def test_update_factura_change_factura_validate_monto_facturas(self):
        """Valida el monto de facturas al reemplazar una factura a una instancia de factura imputada."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        new_factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        factura = instance.facturas.all().order_by('?').first()
        for f in instance.facturas.all().exclude(pk=factura.pk):
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append(
            {'factura': new_factura.pk, 'action': '{"id": ' + str(factura.pk) + ', \"action\": "update"}'}
        )  # Edita una factura
        monto_facturas = instance.monto_facturas - factura.total_sin_imputar + new_factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.monto_facturas, monto_facturas)
        self.assertEqual(response.status_code, 200)

    def test_update_factura_change_factura_validate_nota_de_credito(self):
        """Valida el monto de nota de crédito al reemplazar una factura a una instancia de factura imputada."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        new_factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        _factura = instance.facturas.all().order_by('?').first()
        for f in instance.facturas.all().exclude(pk=_factura.pk):
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        # Edita una factura
        facturas_list.append(
            {'factura': new_factura.pk, 'action': '{"id": ' + str(_factura.pk) + ', \"action\": "update"}'}
        )
        monto_facturas = instance.monto_facturas - _factura.total_sin_imputar + new_factura.total
        # Restablezco la nota de credito
        total_nota_de_credito = instance.nota_de_credito.total + instance.nota_de_credito.monto_imputado
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.monto_nota_de_credito, total_nota_de_credito)
        self.assertEqual(response.status_code, 200)

    def test_update_factura_change_factura_validate_total_facturas(self):
        """Valida el total de factura al reemplazar una factura a una instancia de factura imputada."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        new_factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        _factura = instance.facturas.all().order_by('?').first()
        for f in instance.facturas.all().exclude(pk=_factura.pk):
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        # Edita una factura
        facturas_list.append(
            {'factura': new_factura.pk, 'action': '{"id": ' + str(_factura.pk) + ', \"action\": "update"}'}
        )
        monto_facturas = instance.monto_facturas - _factura.total_sin_imputar + new_factura.total_sin_imputar
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.total_factura, total_factura)
        self.assertEqual(response.status_code, 200)

    def test_update_factura_change_validate_facturas_montos_imputados(self):
        """Valida los montos imputados a las facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        facturas_validate = []
        total_nc = instance.nota_de_credito.total_sin_imputar
        new_factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        _factura = instance.facturas.all().order_by('?').first()

        for factura in instance.facturas.all().order_by('facturas_imputacion'):
            factura_total = get_total_factura(factura.total_sin_imputar, total_nc)
            factura_monto_imputado = factura.total_sin_imputar if factura_total == 0 else total_nc
            total_nc -= factura.total_sin_imputar if total_nc > factura.total_sin_imputar else total_nc
            facturas_validate.append({'id': factura.pk, 'monto_imputado': factura_monto_imputado})
            if _factura == factura:  # Si es la factura a eliminar salteo el ultimo paso
                continue
            facturas_list.append(
                {'factura': factura.pk, 'action': '{"id": ' + str(factura.pk) + ', \"action\": "update"}'}
            )

        # Agrego una nueva factura
        facturas_list.append(
            {'factura': new_factura.pk, 'action': '{"id": ' + str(_factura.pk) + ', \"action\": "update"}'}
        )
        total_nc += _factura.monto_imputado
        factura_total = get_total_factura(new_factura.total, total_nc)
        factura_monto_imputado = new_factura.total if factura_total == 0 else total_nc
        facturas_validate.append({'id': new_factura.pk, 'monto_imputado': factura_monto_imputado})
        monto_facturas = instance.monto_facturas - _factura.total_sin_imputar + new_factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()

        for factura in instance.facturas.all().order_by('facturas_imputacion'):
            self.assertEqual(
                factura.monto_imputado,
                [item for item in facturas_validate if item.get('id') == factura.pk][0].get('monto_imputado'),
            )
        self.assertEqual(response.status_code, 200)

    def test_update_factura_change_validate_nota_de_credito(self):
        """Valida los datos de la nota de credito luego de imputar facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        total_nc = instance.nota_de_credito.total_sin_imputar
        new_factura = FacturaClienteFactory.create(
            tipo='A', cobrado=False, moneda=instance.moneda, cliente=instance.cliente
        )
        _factura = instance.facturas.all().order_by('?').first()  # factura a remplazar
        for factura in instance.facturas.all():
            total_nc -= factura.total_sin_imputar if total_nc > factura.total_sin_imputar else total_nc
            facturas_list.append(
                {'factura': factura.pk, 'action': '{"id": ' + str(factura.pk) + ', \"action\": "update"}'}
            )

        facturas_list.append(
            {'factura': new_factura.pk, 'action': '{"id": ' + str(_factura.pk) + ', \"action\": "update"}'}
        )
        total_nc += _factura.monto_imputado
        total_nc -= new_factura.total_sin_imputar if total_nc > new_factura.total_sin_imputar else total_nc
        monto_facturas = instance.monto_facturas + new_factura.total
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)

        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.nota_de_credito.total, total_nc)
        self.assertEqual(response.status_code, 200)

    def test_update_factura_delete_factura_validate_monto_facturas(self):
        """Valida el monto de facturas al eliminar una factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        # Elimina una factura
        _factura = instance.facturas.all().order_by('?').first()
        for f in instance.facturas.all().exclude(pk=_factura.pk):
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append(
            {'factura': _factura.pk, 'action': '{"id": ' + str(_factura.pk) + ', \"action\": "delete"}'}
        )
        monto_facturas = instance.monto_facturas - _factura.total_sin_imputar
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.monto_facturas, monto_facturas)
        self.assertEqual(response.status_code, 200)

    def test_update_factura_delete_factura_validate_nota_de_credito(self):
        """Valida el monto de nota de credito al eliminar una factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        monto_nota_de_credito = instance.monto_nota_de_credito
        # Elimina una factura
        _factura = instance.facturas.all().order_by('?').first()
        for f in instance.facturas.all().exclude(pk=_factura.pk):
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append(
            {'factura': _factura.pk, 'action': '{"id": ' + str(_factura.pk) + ', \"action\": "delete"}'}
        )
        monto_facturas = instance.monto_facturas - _factura.total_sin_imputar
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.monto_nota_de_credito, monto_nota_de_credito)
        self.assertEqual(response.status_code, 200)

    def test_update_factura_delete_factura_validate_total_facturas(self):
        """Valida el total de facturas al eliminar una factura."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        # Elimina una factura
        _factura = instance.facturas.all().order_by('?').first()
        for f in instance.facturas.all().exclude(pk=_factura.pk):
            facturas_list.append({'factura': f.pk, 'action': '{"id": ' + str(f.pk) + ', \"action\": "update"}'})
        facturas_list.append(
            {'factura': _factura.pk, 'action': '{"id": ' + str(_factura.pk) + ', \"action\": "delete"}'}
        )
        monto_facturas = instance.monto_facturas - _factura.total_sin_imputar
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        self.assertEqual(instance.total_factura, total_factura)
        self.assertEqual(response.status_code, 200)

    def test_update_factura_delete_validate_facturas_montos_imputados(self):
        """Valida los montos imputados a las facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        facturas_validate = []
        total_nc = instance.nota_de_credito.total_sin_imputar
        _factura = (
            instance.facturas.all().order_by('facturas_imputacion').first()
        )  # en frontend no se puede eliminar la primera

        for factura in instance.facturas.all().order_by('facturas_imputacion'):
            factura_total = get_total_factura(factura.total_sin_imputar, total_nc)
            factura_monto_imputado = factura.total_sin_imputar if factura_total == 0 else total_nc
            total_nc -= factura.total_sin_imputar if total_nc > factura.total_sin_imputar else total_nc
            facturas_validate.append({'id': factura.pk, 'monto_imputado': factura_monto_imputado})
            if _factura == factura:
                continue
            facturas_list.append(
                {'factura': factura.pk, 'action': '{"id": ' + str(factura.pk) + ', \"action\": "update"}'}
            )

        facturas_list.append(  # Elimino una factura
            {'factura': _factura.pk, 'action': '{"id": ' + str(_factura.pk) + ', \"action\": "delete"}'}
        )

        monto_facturas = instance.monto_facturas - _factura.total_sin_imputar
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        for factura in instance.facturas.all().order_by('facturas_imputacion'):
            self.assertEqual(
                factura.monto_imputado,
                [item for item in facturas_validate if item.get('id') == factura.pk][0].get('monto_imputado'),
            )
        self.assertEqual(response.status_code, 200)

    def test_update_factura_delete_validate_nota_de_credito(self):
        """Valida los datos de la nota de credito luego de imputar facturas."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        instance = self.instance
        facturas_list = []
        facturas_validate = []
        total_nc = instance.nota_de_credito.total_sin_imputar
        _factura = (
            instance.facturas.all().order_by('facturas_imputacion').last()
        )  # en frontend no se puede eliminar la primera

        for factura in instance.facturas.all().order_by('facturas_imputacion'):
            factura_total = get_total_factura(factura.total_sin_imputar, total_nc)
            factura_monto_imputado = factura.total_sin_imputar if factura_total == 0 else total_nc
            total_nc -= factura.total_sin_imputar if total_nc > factura.total_sin_imputar else total_nc
            facturas_validate.append({'id': factura.pk, 'monto_imputado': factura_monto_imputado})
            if _factura == factura:
                continue
            facturas_list.append(
                {'factura': factura.pk, 'action': '{"id": ' + str(factura.pk) + ', \"action\": "update"}'}
            )

        facturas_list.append(  # Elimino una factura
            {'factura': _factura.pk, 'action': '{"id": ' + str(_factura.pk) + ', \"action\": "delete"}'}
        )

        monto_facturas = instance.monto_facturas - _factura.total_sin_imputar
        total_factura = get_total_factura(monto_facturas, instance.nota_de_credito.total_sin_imputar)
        data = FacturaImputadaClienteFactoryData().update(instance, facturas_list, monto_facturas, total_factura)
        response = self.client.put(f'/api/factura-imputada/{self.instance.pk}/', data, format='json')
        instance.refresh_from_db()
        total_nc += _factura.monto_imputado
        self.assertEqual(instance.nota_de_credito.total, total_nc)
        self.assertEqual(response.status_code, 200)
