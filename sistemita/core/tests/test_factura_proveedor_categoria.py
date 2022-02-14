"""Test categoría factura de proveedores."""

# Django
from django.test import Client
from faker import Faker

# Sistemita
from sistemita.core.forms import FacturaProveedorCategoriaForm
from sistemita.core.models import FacturaProveedorCategoria
from sistemita.core.tests.factories import (
    FacturaProveedorCategoriaFactory,
    FacturaProveedorCategoriaFactoryData,
)
from sistemita.utils.tests import BaseTestCase

fake = Faker('es_ES')


class FacturaProveedorCategoriaTest(BaseTestCase):
    """Tests de categorías de facturas de proveedores."""

    def setUp(self):
        self.data = FacturaProveedorCategoriaFactoryData().build()
        self.instance = FacturaProveedorCategoriaFactory.create()
        self.client = Client()

    def test_string_representation(self):
        """Representación legible del modelo."""
        categoria = self.instance
        self.assertEqual(str(categoria), f'{categoria.nombre}')

    # Listado
    def test_length_in_template(self):
        """Verifica cantidad de categorías en el template listado."""
        count = FacturaProveedorCategoria.objects.count()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertEqual(len(response.context['object_list']), count)

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado de categorias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado de categorias."""
        self.create_user(['list_facturaproveedorcategoria'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedorcategoria_list.html')

    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado de categorias."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta lista categorias."""
        response = self.client.get('/facturaproveedorcategoria/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    # Agregar
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

    # Editar
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

    # Detail
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

    # Delete
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

    # Formulario
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
        if self.instance.nombre != self.data.get('nombre'):
            form.save()
            categoria_2 = FacturaProveedorCategoriaFactoryData().build()
            categoria_2['nombre'] = self.data.get('nombre')
            form = FacturaProveedorCategoriaForm(data=categoria_2)

        self.assertHasProps(
            form.errors,
            [
                'nombre',
            ],
        )
