"""Clientes test."""

# Django
from django.core.management import call_command
from faker import Faker

# Sistemita
from sistemita.core.forms.clientes import ClienteForm
from sistemita.core.models import Cliente
from sistemita.core.tests.factories import ClienteFactory, ClienteFactoryData
from sistemita.utils.tests import BaseTestCase, prevent_request_warnings, randN

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('permissions_translation', verbosity=0)
    call_command('add_permissions', verbosity=0)


class ClienteModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = ClienteFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        cliente = self.instance
        self.assertEqual(str(cliente), f'{cliente.razon_social} - {cliente.cuit}')


class ClienteListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cliente/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado."""
        self.create_user(['list_cliente'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cliente/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cliente/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta listar."""
        response = self.client.get('/cliente/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_length_in_template(self):
        """Verifica cantidad de instancias en el template listado."""
        instance = ClienteFactory.create()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cliente/')
        self.assertQuerysetEqual(response.context['object_list'], [instance], transform=lambda x: x)

    def test_last_created_in_template(self):
        """Verifica cantidad de instancias creadas en la semana."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cliente/')
        self.assertEqual(response.context['last_created'], Cliente.objects.count())

    def test_list_empty(self):
        """Verifica un listado vacío cuando no hay instancias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/factura/')
        self.assertContains(response, 'Sin resultados')


class ClienteCreateViewTest(BaseTestCase):
    """Tests sobre la vista de crear."""

    fixtures = [
        'fixtures/countries.json',
        'fixtures/states.json',
        'fixtures/districts.json',
        'fixtures/localities.json',
    ]

    def setUp(self):
        self.data = ClienteFactoryData().build()

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cliente/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_form.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['add_cliente'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cliente/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_form.html')

    @prevent_request_warnings
    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cliente/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear."""
        response = self.client.get('/cliente/agregar/')
        self.assertEqual(response.status_code, 302)

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que un usuario sin permisos no pueda realizar un post."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/cliente/agregar/')
        self.assertEqual(response.status_code, 403)

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta realizar un post."""
        response = self.client.post('/cliente/agregar/')
        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        form = ClienteForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_form_fields_required(self):
        """Valida los campos requeridos."""
        form = ClienteForm(data={})
        required_fields = ['razon_social', 'cuit', 'correo', 'telefono']
        self.assertHasProps(form.errors, required_fields)

    def test_form_cuit_invalid(self):
        """Valida el cuit."""
        self.data['cuit'] = randN(10)
        form = ClienteForm(data=self.data)
        self.assertFalse(form.is_valid())

    def test_cuit_unique(self):
        """Verifica si el cuit ya está registrado."""
        form = ClienteForm(data=self.data)
        form.save()
        cliente_2 = ClienteFactoryData().build()
        cliente_2['cuit'] = self.data.get('cuit')
        form_2 = ClienteForm(data=cliente_2)
        self.assertHasProps(
            form_2.errors,
            [
                'cuit',
            ],
        )

    def test_correo_unique(self):
        """Verifica si el email ya está registrado."""
        form = ClienteForm(data=self.data)
        form.save()
        cliente_2 = ClienteFactoryData().build()
        cliente_2['correo'] = self.data.get('correo')
        form_2 = ClienteForm(data=cliente_2)
        self.assertHasProps(
            form_2.errors,
            [
                'correo',
            ],
        )

    def test_link_envio_factura_invalid(self):
        """Valida el link de envío con el formato correcto."""
        cliente = self.data
        cliente['link_envio_factura'] = fake.first_name()
        form = ClienteForm(data=cliente)
        self.assertHasProps(
            form.errors,
            [
                'link_envio_factura',
            ],
        )

    def test_tipo_envio_factura_invalid(self):
        """Valida el tipo de envío con el formato correcto."""
        cliente = self.data
        cliente['tipo_envio_factura'] = fake.bothify(letters='xyz')
        form = ClienteForm(data=cliente)
        self.assertHasProps(
            form.errors,
            [
                'tipo_envio_factura',
            ],
        )

    def test_correo_invalid(self):
        """Valida el correo con el formato correcto."""
        cliente = self.data
        cliente['correo'] = fake.first_name()
        form = ClienteForm(data=cliente)
        self.assertHasProps(
            form.errors,
            [
                'correo',
            ],
        )


class ClienteDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = ClienteFactory.create()

    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/cliente/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['view_cliente'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_detail.html')

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar."""
        response = self.client.get(f'/cliente/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class ClienteUpdateViewTest(BaseTestCase):
    """Test sobre la vista de editar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = ClienteFactory.create()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/cliente/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_form.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar."""
        self.create_user(['change_cliente'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_form.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.get(f'/cliente/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post(f'/cliente/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.post(f'/cliente/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class ClienteDeleteViewTest(BaseTestCase):
    """Test sobre la vista de eliminar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = ClienteFactory.create()

    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/cliente/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar."""
        self.create_user(['delete_cliente'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_confirm_delete.html')

    @prevent_request_warnings
    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.get(f'/cliente/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_detroy_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.delete(f'/cliente/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detroy_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.delete(f'/cliente/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')
