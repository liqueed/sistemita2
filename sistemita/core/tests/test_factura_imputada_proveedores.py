"""Factura imputada proveedor test."""

# Django
from django.core.management import call_command
from faker import Faker

from sistemita.core.constants import ZERO_DECIMAL

# Sistemita
from sistemita.core.models import FacturaProveedor
from sistemita.core.tests.factories import (
    FacturaImputadaProveedorFactory,
    FacturaProveedorFactory,
)
from sistemita.utils.tests import BaseTestCase, prevent_request_warnings

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class FacturaImputadaProveedorModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = FacturaImputadaProveedorFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        factura = self.instance
        self.assertEqual(str(factura), f'{factura.fecha} | {factura.proveedor} | {factura.total_factura}')


class FacturaImputadaProveedorListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/facturaproveedorimputada/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorimputada_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado."""
        self.create_user(['list_facturaproveedorimputada'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/facturaproveedorimputada/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorimputada_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/facturaproveedorimputada/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta listar."""
        response = self.client.get('/facturaproveedorimputada/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_length_in_template(self):
        """Verifica cantidad de instancias en el template listado."""
        instance = FacturaImputadaProveedorFactory.create()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/facturaproveedorimputada/')
        self.assertQuerysetEqual(response.context['object_list'], [instance], transform=lambda x: x)

    def test_list_empty(self):
        """Verifica un listado vacío cuando no hay instancias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/facturaproveedorimputada/')
        self.assertContains(response, 'Sin resultados')


class FacturaImputadaClienteCreateViewTest(BaseTestCase):
    """Tests sobre la vista de crear."""

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/facturaproveedorimputada/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorimputada_create.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['add_facturaproveedorimputada'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/facturaproveedorimputada/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorimputada_create.html')

    @prevent_request_warnings
    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/facturaproveedorimputada/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear."""
        response = self.client.get('/facturaproveedorimputada/agregar/')
        self.assertEqual(response.status_code, 302)


class FacturaImputadaClienteDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = FacturaImputadaProveedorFactory.create()

    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorimputada_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['view_facturaproveedorimputada'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorimputada_detail.html')

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar."""
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class FacturaImputadaClienteUpdateViewTest(BaseTestCase):
    """Test sobre la vista de editar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = FacturaImputadaProveedorFactory.create()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorimputada_update.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar."""
        self.create_user(['change_facturaproveedorimputada'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorimputada_update.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class FacturaImputadaClienteDeleteViewTest(BaseTestCase):
    """Test sobre la vista de eliminar."""

    def setUp(self):
        """Creación de instancia."""
        facturas = []
        for _ in range(0, 2):
            factura = FacturaProveedorFactory.create(tipo='A', cobrado=False)
            facturas.append(factura)
        self.instance = FacturaImputadaProveedorFactory.create(facturas=facturas)

    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorimputada_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar."""
        self.create_user(['delete_facturaproveedorimputada'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorimputada_confirm_delete.html')

    @prevent_request_warnings
    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.get(f'/facturaproveedorimputada/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_detroy_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.delete(f'/facturaproveedorimputada/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detroy_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.delete(f'/facturaproveedorimputada/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_detroy_restore_nota_de_credito(self):
        """Al eliminar una factura imputada la nota de crédito debe reestablecerse."""
        self.create_user(['delete_facturaproveedorimputada'])
        self.client.login(username='user', password='user12345')
        nota_de_credito = FacturaProveedor.objects.get(pk=self.instance.nota_de_credito.pk)
        monto_nota_de_credito = nota_de_credito.total_sin_imputar
        self.client.delete(f'/facturaproveedorimputada/{self.instance.pk}/eliminar/')
        nota_de_credito.refresh_from_db()
        self.assertFalse(nota_de_credito.cobrado)
        self.assertEqual(nota_de_credito.total, monto_nota_de_credito)
        self.assertEqual(nota_de_credito.monto_imputado, ZERO_DECIMAL)

    def test_detroy_restore_facturas(self):
        """Al eliminar una factura imputada las facturas deben ser reestablecidas."""
        self.create_user(['delete_facturaproveedorimputada'])
        self.client.login(username='user', password='user12345')
        facturas = [FacturaProveedor.objects.get(pk=factura.pk) for factura in self.instance.facturas.all()]
        self.client.delete(f'/facturaproveedorimputada/{self.instance.pk}/eliminar/')
        for factura in facturas:
            factura.refresh_from_db()
            self.assertFalse(factura.cobrado)
            self.assertEqual(factura.total, factura.total_sin_imputar)
            self.assertEqual(factura.monto_imputado, ZERO_DECIMAL)
