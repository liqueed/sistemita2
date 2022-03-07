"""Test categoría factura de proveedores."""

# Django
from django.core.management import call_command
from faker import Faker

# Sistemita
from sistemita.core.forms import FacturaProveedorCategoriaForm
from sistemita.core.models import FacturaProveedorCategoria
from sistemita.core.tests.factories import (
    FacturaProveedorCategoriaFactory,
    FacturaProveedorCategoriaFactoryData,
)
from sistemita.utils.tests import BaseTestCase, prevent_request_warnings

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class FacturaProveedorCategoriaModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = FacturaProveedorCategoriaFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        categoria = self.instance
        self.assertEqual(str(categoria), f'{categoria.nombre}')


class FacturaProveedorCategoriaListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado."""
        self.create_user(['list_facturaproveedorcategoria'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta listar."""
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_length_in_template(self):
        """Verifica cantidad de categorías en el template listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        instance = FacturaProveedorCategoriaFactory.create()
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertQuerysetEqual(response.context['object_list'], [instance], transform=lambda x: x)

    def test_last_created_in_template(self):
        """Verifica cantidad de instancias creadas en la semana."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        FacturaProveedorCategoriaFactory.create()
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertEqual(response.context['last_created'], FacturaProveedorCategoria.objects.count())

    def test_list_empty(self):
        """Verifica un listado vacío cuando no hay instancias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertContains(response, 'Sin resultados')


class FacturaProveedorCategoriaCreateViewTest(BaseTestCase):
    """Tests sobre la vista de crear."""

    def setUp(self):
        self.data = FacturaProveedorCategoriaFactoryData().build()

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear categorias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/facturaproveedorcategoria/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_form.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar categorias."""
        self.create_user(['add_facturaproveedorcategoria'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/facturaproveedorcategoria/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_form.html')

    @prevent_request_warnings
    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear categorias."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/facturaproveedorcategoria/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear categorias."""
        response = self.client.get('/facturaproveedorcategoria/agregar/')
        self.assertEqual(response.status_code, 302)

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que un usuario sin permisos no pueda realizar un post."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/facturaproveedorcategoria/agregar/')
        self.assertEqual(response.status_code, 403)

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta realizar un post."""
        response = self.client.post('/facturaproveedorcategoria/agregar/')
        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        form = FacturaProveedorCategoriaForm(data={'nombre': 'Categoría única'})
        self.assertTrue(form.is_valid())

    def test_form_fields_required(self):
        """Valida los campos requeridos."""
        form = FacturaProveedorCategoriaForm(data={})
        required_fields = ['nombre']
        self.assertHasProps(form.errors, required_fields)

    def test_nombre_unique(self):
        """Verifica si el nombre ya está registrado."""
        form = FacturaProveedorCategoriaForm(data=self.data)
        form.save()
        categoria_2 = FacturaProveedorCategoriaFactoryData().build()
        categoria_2['nombre'] = self.data.get('nombre')
        form2 = FacturaProveedorCategoriaForm(data=categoria_2)

        self.assertHasProps(
            form2.errors,
            [
                'nombre',
            ],
        )


class FacturaProveedorCategoriaDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = FacturaProveedorCategoriaFactory.create()

    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar categorias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar categorias."""
        self.create_user(['view_facturaproveedorcategoria'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_detail.html')

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar categorias."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar categorias."""
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class FacturaProveedorCategoriaUpdateViewTest(BaseTestCase):
    """Test sobre la vista de editar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = FacturaProveedorCategoriaFactory.create()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar categorias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_form.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar categorias."""
        self.create_user(['change_facturaproveedorcategoria'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_form.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar categorias."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar categorias."""
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post(f'/facturaproveedorcategoria/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.post(f'/facturaproveedorcategoria/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class FacturaProveedorCategoriaDeleteViewTest(BaseTestCase):
    """Test sobre la vista de eliminar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = FacturaProveedorCategoriaFactory.create()

    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar categorias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar categorias."""
        self.create_user(['delete_facturaproveedorcategoria'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_confirm_delete.html')

    @prevent_request_warnings
    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar categorias."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar categorias."""
        response = self.client.get(f'/facturaproveedorcategoria/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_detroy_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.delete(f'/facturaproveedorcategoria/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detroy_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.delete(f'/facturaproveedorcategoria/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')
