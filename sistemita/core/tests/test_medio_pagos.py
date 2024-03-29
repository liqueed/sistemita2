"""Test medios de pagos."""

# Django
from django.core.management import call_command
from faker import Faker

# Sistemita
from sistemita.core.forms import MedioPagoForm
from sistemita.core.models import MedioPago
from sistemita.core.tests.factories import (
    MedioPagoFactory,
    MedioPagoFactoryData,
)
from sistemita.utils.tests import BaseTestCase, prevent_request_warnings

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class MedioPagoModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = MedioPagoFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        mediopago = self.instance
        self.assertEqual(str(mediopago), f'{mediopago.nombre}')


class MedioPagoListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado de medios de pagos."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/mediopago/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/mediopago_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado de medios de pagos."""
        self.create_user(['list_mediopago'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/mediopago/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/mediopago_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado de medios de pagos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/mediopago/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta lista clientes."""
        response = self.client.get('/cliente/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_length_in_template(self):
        """Verifica cantidad de medio de pago en el template listado."""
        MedioPagoFactory.create()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/mediopago/')
        self.assertEqual(len(response.context['object_list']), MedioPago.objects.count())

    def test_last_created_in_template(self):
        """Verifica cantidad de instancias creadas en la semana."""
        MedioPagoFactory.create()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/mediopago/')
        self.assertEqual(response.context['last_created'], MedioPago.objects.count())

    def test_list_empty(self):
        """Verifica un listado vacío cuando no hay instancias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/mediopago/')
        self.assertContains(response, 'Sin resultados')


class MedioPagoCreateViewTest(BaseTestCase):
    """Tests sobre la vista de crear."""

    def setUp(self):
        self.data = MedioPagoFactoryData().build()

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear medios de pagos."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/mediopago/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/mediopago_form.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar medios de pagos."""
        self.create_user(['add_mediopago'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/mediopago/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/mediopago_form.html')

    @prevent_request_warnings
    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear medios de pagos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/mediopago/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear medios de pagos."""
        response = self.client.get('/mediopago/agregar/')
        self.assertEqual(response.status_code, 302)

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que un usuario sin permisos no pueda realizar un post."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/mediopago/agregar/')
        self.assertEqual(response.status_code, 403)

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta realizar un post."""
        response = self.client.post('/mediopago/agregar/')
        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        form = MedioPagoForm(data={'nombre': 'Nombre único'})
        self.assertTrue(form.is_valid())

    def test_form_fields_required(self):
        """Valida los campos requeridos."""
        form = MedioPagoForm(data={})
        required_fields = ['nombre']
        self.assertHasProps(form.errors, required_fields)

    def test_nombre_unique(self):
        """Verifica si el nombre ya está registrado."""
        form = MedioPagoForm(data=self.data)
        form.save()
        medio_2 = MedioPagoFactoryData().build()
        medio_2['nombre'] = self.data.get('nombre')
        form2 = MedioPagoForm(data=medio_2)
        self.assertHasProps(
            form2.errors,
            [
                'nombre',
            ],
        )


class MedioPagoDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = MedioPagoFactory.create()

    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar medios de pagos."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/mediopago/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/mediopago_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar medios de pagos."""
        self.create_user(['view_mediopago'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/mediopago/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/mediopago_detail.html')

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar medios de pagos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/mediopago/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar medios de pagos."""
        response = self.client.get(f'/mediopago/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class MedioPagoUpdateViewTest(BaseTestCase):
    """Test sobre la vista de editar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = MedioPagoFactory.create()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar medios de pagos."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/mediopago/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/mediopago_form.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar medios de pagos."""
        self.create_user(['change_mediopago'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/mediopago/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/mediopago_form.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar medios de pagos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/mediopago/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar medios de pagos."""
        response = self.client.get(f'/mediopago/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post(f'/mediopago/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.post(f'/mediopago/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class MedioPagoDeleteViewTest(BaseTestCase):
    """Test sobre la vista de eliminar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = MedioPagoFactory.create()

    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar medios de pagos."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/mediopago/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/mediopago_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar medios de pagos."""
        self.create_user(['delete_mediopago'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/mediopago/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/mediopago_confirm_delete.html')

    @prevent_request_warnings
    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar medios de pagos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/mediopago/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar medios de pagos."""
        response = self.client.get(f'/mediopago/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_detroy_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.delete(f'/mediopago/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detroy_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.delete(f'/mediopago/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')
