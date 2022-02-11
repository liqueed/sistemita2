"""Users test."""

# Django
from django.test import Client
from faker import Faker

# Sistemita
from sistemita.core.forms.clientes import ClienteForm
from sistemita.core.models import Cliente
from sistemita.core.tests.factories import ClienteFactory, ClienteFactoryData
from sistemita.utils.tests import BaseTestCase, randN

fake = Faker('es_ES')


class ClienteTest(BaseTestCase):
    """ClienteTest class."""

    def setUp(self):
        self.data = ClienteFactoryData().build()
        self.instance = ClienteFactory.create()
        self.client = Client()

    def test_string_representation(self):
        """Representación legible del modelo."""
        cliente = self.instance
        self.assertEqual(str(cliente), f'{cliente.razon_social} - {cliente.cuit}')

    # Listado
    def test_length_in_template(self):
        """Verifica cantidad de clientes en el template listado."""
        count = Cliente.objects.count()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cliente/')
        self.assertEqual(len(response.context['object_list']), count)

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado de clientes."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cliente/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado de clientes."""
        self.create_user(['list_cliente'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cliente/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_list.html')

    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado de clientes."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cliente/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta lista clientes."""
        response = self.client.get('/cliente/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    # Agregar
    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear clientes."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/cliente/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_form.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar clientes."""
        self.create_user(['add_cliente'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cliente/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_form.html')

    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear clientes."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/cliente/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear clientes."""
        response = self.client.get('/cliente/agregar/')
        self.assertEqual(response.status_code, 302)

    # Editar
    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar clientes."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/cliente/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_form.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar clientes."""
        self.create_user(['change_cliente'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_form.html')

    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar clientes."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar clientes."""
        response = self.client.get(f'/cliente/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    # Detail
    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar clientes."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/cliente/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar clientes."""
        self.create_user(['view_cliente'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_detail.html')

    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar clientes."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar clientes."""
        response = self.client.get(f'/cliente/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    # Delete
    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar clientes."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/cliente/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar clientes."""
        self.create_user(['delete_cliente'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/cliente_confirm_delete.html')

    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar clientes."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/cliente/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar clientes."""
        response = self.client.get(f'/cliente/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    # Formulario
    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        form = ClienteForm(data=self.data)
        self.assertTrue(form.is_valid())

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
