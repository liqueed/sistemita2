"""Test medios de pagos."""

# Django
from django.test import Client
from faker import Faker

# Sistemita
from sistemita.core.forms import MedioPagoForm
from sistemita.core.models import MedioPago
from sistemita.core.tests.factories import (
    MedioPagoFactory,
    MedioPagoFactoryData,
)
from sistemita.utils.tests import BaseTestCase

fake = Faker('es_ES')


class MedioPagoTest(BaseTestCase):
    """ "Medio de pagos tests."""

    def setUp(self):
        self.data = MedioPagoFactoryData().build()
        self.instance = MedioPagoFactory.create()
        self.client = Client()

    def test_string_representation(self):
        """Representación legible del modelo."""
        mediopago = self.instance
        self.assertEqual(str(mediopago), f'{mediopago.nombre}')

    # Listado
    def test_length_in_template(self):
        """Verifica cantidad de medio de pago en el template listado."""
        count = MedioPago.objects.count()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/mediopago/')
        self.assertEqual(len(response.context['object_list']), count)

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

    # Agregar
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

    # Editar
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

    # Detail
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

    # Delete
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

    # Formulario
    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        form = MedioPagoForm(data=self.data)
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
        cliente_2 = MedioPagoFactoryData().build()
        cliente_2['nombre'] = self.data.get('nombre')
        form_2 = MedioPagoForm(data=cliente_2)
        self.assertHasProps(
            form_2.errors,
            [
                'nombre',
            ],
        )
