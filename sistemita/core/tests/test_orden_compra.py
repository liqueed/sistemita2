"""Test orden de compras de clientes."""

# Django
from django.test import Client
from faker import Faker

# Sistemita
from sistemita.core.forms import OrdenCompraForm
from sistemita.core.models import OrdenCompra
from sistemita.core.tests.factories import (
    OrdenCompraFactory,
    OrdenCompraFactoryData,
)
from sistemita.utils.tests import BaseTestCase, rand_element_from_array

fake = Faker('es_ES')


class OrdenCompraTest(BaseTestCase):
    """Test del modelo de orden compra de clientes."""

    def setUp(self):
        self.data = OrdenCompraFactoryData().build()
        self.instance = OrdenCompraFactory.create()
        self.client = Client()

    def test_string_representation(self):
        """Representación legible del modelo."""
        orden_compra = self.instance
        self.assertEqual(str(orden_compra), f'{orden_compra.fecha} | {orden_compra.cliente}')

    # Listado
    def test_length_in_template(self):
        """Verifica cantidad de ordenes de pago en el template listado."""
        count = OrdenCompra.objects.count()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/ordencompra/')
        self.assertEqual(len(response.context['object_list']), count)

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado de ordenes de compras."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/ordencompra/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/ordencompra_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado de ordenes de compras."""
        self.create_user(['list_ordencompra'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/ordencompra/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/ordencompra_list.html')

    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado de ordenes de compras."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/ordencompra/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta lista clientes."""
        response = self.client.get('/cliente/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    # Agregar
    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear ordenes de compras."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/ordencompra/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/ordencompra_form.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar ordenes de compras."""
        self.create_user(['add_ordencompra'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/ordencompra/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/ordencompra_form.html')

    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear ordenes de compras."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/ordencompra/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear ordenes de compras."""
        response = self.client.get('/ordencompra/agregar/')
        self.assertEqual(response.status_code, 302)

    # Editar
    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar ordenes de compras."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/ordencompra/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/ordencompra_form.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar ordenes de compras."""
        self.create_user(['change_ordencompra'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/ordencompra/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/ordencompra_form.html')

    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar ordenes de compras."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/ordencompra/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar ordenes de compras."""
        response = self.client.get(f'/ordencompra/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    # Detail
    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar ordenes de compras."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/ordencompra/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/ordencompra_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar ordenes de compras."""
        self.create_user(['view_ordencompra'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/ordencompra/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/ordencompra_detail.html')

    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar ordenes de compras."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/ordencompra/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar ordenes de compras."""
        response = self.client.get(f'/ordencompra/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    # Delete
    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar ordenes de compras."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/ordencompra/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/ordencompra_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar ordenes de compras."""
        self.create_user(['delete_ordencompra'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/ordencompra/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/ordencompra_confirm_delete.html')

    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar ordenes de compras."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/ordencompra/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar ordenes de compras."""
        response = self.client.get(f'/ordencompra/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    # Formulario
    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        form = OrdenCompraForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_form_fields_required(self):
        """Valida los campos requeridos."""
        form = OrdenCompraForm(data={})
        required_fields = ['fecha', 'cliente', 'moneda', 'monto']
        self.assertHasProps(form.errors, required_fields)

    def test_fecha_format_valid(self):
        """Valida el formato de fecha."""
        data_invalid = ['03/28/2022', '03/02/22', 'Text', '11/08', '']
        self.data['fecha'] = rand_element_from_array(data_invalid)
        form = OrdenCompraForm(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertHasProps(form.errors, ['fecha'])

    def test_monto_format_valid(self):
        """Valida el formato del monto."""
        data_invalid = [-1.0, 'text']
        self.data['monto'] = rand_element_from_array(data_invalid)
        form = OrdenCompraForm(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertHasProps(form.errors, ['monto'])
