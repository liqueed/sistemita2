"""Cobranzas test."""

# Django
from django.core.management import call_command
from faker import Faker

# Sistemita
from sistemita.accounting.models import Cobranza
from sistemita.accounting.tests.factories import (
    CobranzaFactory,
    CobranzaFacturaFactory,
    CobranzaFacturaPagoFactory,
)
from sistemita.utils.tests import BaseTestCase, prevent_request_warnings

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class CobranzaModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = CobranzaFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        cobranza = self.instance
        self.assertEqual(str(cobranza), f'{cobranza.fecha} - {cobranza.cliente} - {cobranza.moneda} {cobranza.total}')


class CobranzaFacturaModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = CobranzaFacturaFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        cobranza_factura = self.instance
        self.assertEqual(
            str(cobranza_factura),
            (
                f'{cobranza_factura.factura.fecha} - {cobranza_factura.factura.cliente} - '
                f'{cobranza_factura.factura.moneda_monto}'
            ),
        )


class CobranzaFacturaPagoModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = CobranzaFacturaPagoFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        cobranza_factura_pago = self.instance
        self.assertEqual(
            str(cobranza_factura_pago),
            (
                f'{cobranza_factura_pago.metodo} - {cobranza_factura_pago.cobranza_factura.cobranza.moneda} '
                f'{cobranza_factura_pago.monto}'
            ),
        )


class CobranzaListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cobranza/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='accounting/cobranza_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado."""
        self.create_user(['list_cobranza'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cobranza/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='accounting/cobranza_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cobranza/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta listar."""
        response = self.client.get('/cobranza/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_length_in_template(self):
        """Verifica cantidad de instancias en el template listado."""
        instance = CobranzaFactory.create()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cobranza/')
        self.assertQuerysetEqual(response.context['object_list'], [instance], transform=lambda x: x)

    def test_last_created_in_template(self):
        """Verifica cantidad de instancias creadas en la semana."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cobranza/')
        self.assertEqual(response.context['last_created'], Cobranza.objects.count())

    def test_list_empty(self):
        """Verifica un listado vacío cuando no hay instancias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cobranza/')
        self.assertContains(response, 'Sin resultados')


class CobranzaCreateViewTest(BaseTestCase):
    """Tests sobre la vista de crear."""

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cobranza/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='accounting/cobranza_create.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['add_cobranza'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cobranza/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='accounting/cobranza_create.html')

    @prevent_request_warnings
    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cobranza/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear."""
        response = self.client.get('/cobranza/agregar/')
        self.assertEqual(response.status_code, 302)


class CobranzaDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = CobranzaFactory.create()

    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/cobranza/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='accounting/cobranza_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['view_cobranza'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cobranza/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='accounting/cobranza_detail.html')

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cobranza/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar."""
        response = self.client.get(f'/cobranza/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class CobranzaUpdateViewTest(BaseTestCase):
    """Test sobre la vista de editar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = CobranzaFactory.create()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/cobranza/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='accounting/cobranza_update.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar."""
        self.create_user(['change_cobranza'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cobranza/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='accounting/cobranza_update.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cobranza/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.get(f'/cobranza/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class CobranzaDeleteViewTest(BaseTestCase):
    """Test sobre la vista de eliminar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = CobranzaFactory.create()
        for _ in range(0, 2):
            CobranzaFacturaFactory.create(cobranza=self.instance)

    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/cobranza/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='accounting/cobranza_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar."""
        self.create_user(['delete_cobranza'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cobranza/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='accounting/cobranza_confirm_delete.html')

    @prevent_request_warnings
    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cobranza/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.get(f'/cobranza/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_detroy_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.delete(f'/cobranza/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detroy_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.delete(f'/cobranza/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_detroy_restore_facturas(self):
        """
        Al eliminar una cobranza las facturas deben pasar a estar como no cobradas y sus fondos asociados
        a no disponibles.
        """
        self.create_user(['delete_cobranza'])
        self.client.login(username='user', password='user12345')
        facturas = self.instance.cobranza_facturas.all()
        response = self.client.delete(f'/cobranza/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        result = 0
        for factura in facturas:
            result += factura.cobrado
            result += factura.factura_fondo.disponible
        self.assertFalse(result)
