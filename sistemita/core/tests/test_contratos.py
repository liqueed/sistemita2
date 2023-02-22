"""Test orden de compras de clientes."""

# Django
from django.core.management import call_command
from faker import Faker

# Sistemita
from sistemita.core.forms import ContratoForm
from sistemita.core.models import Contrato
from sistemita.core.tests.factories import ContratoFactory, ContratoFactoryData
from sistemita.utils.tests import (
    BaseTestCase,
    prevent_request_warnings,
    rand_element_from_array,
)

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class ContratoModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = ContratoFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        contrato = self.instance
        self.assertEqual(str(contrato), f'{contrato.fecha_desde} | {contrato.cliente}')


class ContratoListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado de ordenes de compras."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/contrato/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/contrato_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado de ordenes de compras."""
        self.create_user(['list_contrato'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/contrato/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/contrato_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado de ordenes de compras."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/contrato/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta lista clientes."""
        response = self.client.get('/contrato/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_length_in_template(self):
        """Verifica cantidad de instancias en el template listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        instance = ContratoFactory.create()
        response = self.client.get('/contrato/')
        self.assertQuerysetEqual(response.context['object_list'], [instance], transform=lambda x: x)

    def test_last_created_in_template(self):
        """Verifica cantidad de instancias creadas en la semana."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        ContratoFactory.create()
        response = self.client.get('/contrato/')
        self.assertEqual(response.context['last_created'], Contrato.objects.count())

    def test_list_empty(self):
        """Verifica un listado vacío cuando no hay instancias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/contrato/')
        self.assertContains(response, 'Sin resultados')


class ContratoCreateViewTest(BaseTestCase):
    """Tests sobre la vista de crear."""

    def setUp(self):
        self.data = ContratoFactoryData().build()

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear ordenes de compras."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/contrato/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/contrato_form.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar ordenes de compras."""
        self.create_user(['add_contrato'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/contrato/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/contrato_form.html')

    @prevent_request_warnings
    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear ordenes de compras."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/contrato/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear ordenes de compras."""
        response = self.client.get('/contrato/agregar/')
        self.assertEqual(response.status_code, 302)

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que un usuario sin permisos no pueda realizar un post."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/contrato/agregar/')
        self.assertEqual(response.status_code, 403)

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta realizar un post."""
        response = self.client.post('/contrato/agregar/')
        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        form = ContratoForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_form_fields_required(self):
        """Valida los campos requeridos."""
        form = ContratoForm(data={})
        required_fields = ['fecha_desde', 'cliente', 'moneda', 'monto']
        self.assertHasProps(form.errors, required_fields)

    def test_fecha_desde_format_valid(self):
        """Valida el formato de fecha."""
        data_invalid = ['03/28/2022', '03/02/22', 'Text', '11/08', '']
        self.data['fecha_desde'] = rand_element_from_array(data_invalid)
        form = ContratoForm(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertHasProps(form.errors, ['fecha_desde'])

    def test_monto_format_valid(self):
        """Valida el formato del monto."""
        data_invalid = [-1.0, 'text']
        self.data['monto'] = rand_element_from_array(data_invalid)
        form = ContratoForm(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertHasProps(form.errors, ['monto'])


class ContratoDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = ContratoFactory.create()

    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar ordenes de compras."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/contrato/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/contrato_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar ordenes de compras."""
        self.create_user(['view_contrato'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/contrato/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/contrato_detail.html')

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar ordenes de compras."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/contrato/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar ordenes de compras."""
        response = self.client.get(f'/contrato/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class ContratoUpdateViewTest(BaseTestCase):
    """Test sobre la vista de editar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = ContratoFactory.create()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar ordenes de compras."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/contrato/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/contrato_form.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar ordenes de compras."""
        self.create_user(['change_contrato'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/contrato/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/contrato_form.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar ordenes de compras."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/contrato/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar ordenes de compras."""
        response = self.client.get(f'/contrato/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post(f'/contrato/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.post(f'/contrato/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class ContratoDeleteViewTest(BaseTestCase):
    """Test sobre la vista de eliminar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = ContratoFactory.create()

    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar ordenes de compras."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/contrato/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/contrato_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar ordenes de compras."""
        self.create_user(['delete_contrato'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/contrato/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/contrato_confirm_delete.html')

    @prevent_request_warnings
    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar ordenes de compras."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/contrato/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar ordenes de compras."""
        response = self.client.get(f'/contrato/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_detroy_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.delete(f'/contrato/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detroy_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.delete(f'/contrato/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')
