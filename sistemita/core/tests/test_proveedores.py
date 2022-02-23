"""Users test."""

# Django
from django.core.management import call_command
from faker import Faker

# Sistemita
from sistemita.core.forms.proveedores import ProveedorForm
from sistemita.core.models import Proveedor
from sistemita.core.tests.factories import (
    ProveedorFactory,
    ProveedorFactoryData,
)
from sistemita.utils.tests import (
    BaseTestCase,
    prevent_request_warnings,
    rand_range,
    randN,
)

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('permissions_translation', verbosity=0)
    call_command('add_permissions', verbosity=0)


class ProveedorModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = ProveedorFactory.build()

    def test_string_representation(self):
        """Representación legible del model modelo."""
        proveedor = self.instance
        self.assertEqual(str(proveedor), f'{proveedor.razon_social} - {proveedor.cuit}')


class ProveedorListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def setUp(self):
        self.instance = ProveedorFactory.create()

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/proveedor/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/proveedor_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado."""
        self.create_user(['list_proveedor'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/proveedor/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/proveedor_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/proveedor/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta lista."""
        response = self.client.get('/proveedor/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_length_in_template(self):
        """Verifica cantidad en el template listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/proveedor/')
        self.assertQuerysetEqual(response.context['object_list'], [self.instance], transform=lambda x: x)

    def test_last_created_in_template(self):
        """Verifica cantidad de instancias creadas en la semana."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/proveedor/')
        self.assertEqual(response.context['last_created'], Proveedor.objects.count())


class ProveedorCreateViewTest(BaseTestCase):
    """Tests sobre la vista de crear."""

    fixtures = [
        'fixtures/countries.json',
        'fixtures/states.json',
        'fixtures/districts.json',
        'fixtures/localities.json',
    ]

    def setUp(self):
        self.data = ProveedorFactoryData().build()

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/proveedor/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/proveedor_form.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['add_proveedor'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/proveedor/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/proveedor_form.html')

    @prevent_request_warnings
    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/proveedor/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear."""
        response = self.client.get('/proveedor/agregar/')
        self.assertEqual(response.status_code, 302)

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que un usuario sin permisos no pueda realizar un post."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/proveedor/agregar/')
        self.assertEqual(response.status_code, 403)

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta realizar un post."""
        response = self.client.post('/proveedor/agregar/')
        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        form = ProveedorForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_form_fields_required(self):
        """Valida los campos requeridos."""
        form = ProveedorForm(data={})
        required_fields = ['razon_social', 'cuit', 'correo', 'telefono']
        self.assertHasProps(form.errors, required_fields)

    def test_form_cuit_invalid(self):
        """Valida el cuit."""
        self.data['cuit'] = randN(10)
        form = ProveedorForm(data=self.data)
        self.assertFalse(form.is_valid())

    def test_cuit_unique(self):
        """Verifica si el cuit ya está registrado."""
        form = ProveedorForm(data=self.data)
        form.is_valid()
        form.save()
        proveedor_2 = ProveedorFactoryData().build()
        proveedor_2['cuit'] = self.data.get('cuit')
        form_2 = ProveedorForm(data=proveedor_2)
        self.assertHasProps(
            form_2.errors,
            [
                'cuit',
            ],
        )

    def test_correo_unique(self):
        """Verifica si el email ya está registrado."""
        form = ProveedorForm(data=self.data)
        form.is_valid()
        form.save()
        proveedor_2 = ProveedorFactoryData().build()
        proveedor_2['correo'] = self.data.get('correo')
        form_2 = ProveedorForm(data=proveedor_2)
        self.assertHasProps(
            form_2.errors,
            [
                'correo',
            ],
        )

    def test_cbu_invalid(self):
        """Valida cbu con el formato correcto."""
        proveedor = self.data
        proveedor['cbu'] = randN(rand_range(23, 30))
        form = ProveedorForm(data=proveedor)
        self.assertHasProps(
            form.errors,
            [
                'cbu',
            ],
        )

    def test_correo_invalid(self):
        """Valida el correo con el formato correcto."""
        proveedor = self.data
        proveedor['correo'] = fake.first_name()
        form = ProveedorForm(data=proveedor)
        self.assertHasProps(
            form.errors,
            [
                'correo',
            ],
        )


class ProveedorDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = ProveedorFactory.create()

    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar proveedores."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/proveedor/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/proveedor_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar proveedores."""
        self.create_user(['view_proveedor'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/proveedor/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/proveedor_detail.html')

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar proveedores."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/proveedor/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar proveedores."""
        response = self.client.get(f'/proveedor/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class ProveedorUpdateViewTest(BaseTestCase):
    """Test sobre la vista de editar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = ProveedorFactory.create()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar proveedores."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/proveedor/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/proveedor_form.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar proveedores."""
        self.create_user(['change_proveedor'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/proveedor/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/proveedor_form.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar proveedores."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/proveedor/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar proveedores."""
        response = self.client.get(f'/proveedor/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post(f'/proveedor/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.post(f'/proveedor/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class ProveedorDeleteViewTest(BaseTestCase):
    """Test sobre la vista de eliminar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = ProveedorFactory.create()

    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/proveedor/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/proveedor_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar."""
        self.create_user(['delete_proveedor'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/proveedor/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/proveedor_confirm_delete.html')

    @prevent_request_warnings
    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/proveedor/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.get(f'/proveedor/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_detroy_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.delete(f'/proveedor/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detroy_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.delete(f'/proveedor/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')
