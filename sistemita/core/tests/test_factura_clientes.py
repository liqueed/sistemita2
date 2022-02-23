"""Factura de Cliente tests."""

# Django
from django.core.management import call_command
from faker import Faker

# Sistemita
from sistemita.core.forms.clientes import FacturaForm
from sistemita.core.models import Factura
from sistemita.core.tests.factories import (
    FacturaClienteFactory,
    FacturaClienteFactoryData,
)
from sistemita.expense.models import Fondo
from sistemita.utils.tests import BaseTestCase, prevent_request_warnings

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class FacturaClienteModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = FacturaClienteFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        factura = self.instance
        self.assertEqual(
            str(factura),
            f'{factura.fecha} - {factura.numero} - {factura.cliente.razon_social} - {factura.moneda_monto}',
        )

    def test_porcentaje_fondo_monto(self):
        """Valida el monto del porcentaje del fondo."""
        factura = self.instance
        monto = round(float(factura.total) * factura.porcentaje_fondo / 100, 2)
        self.assertEqual(self.instance.porcentaje_fondo_monto, monto)


class FacturaClienteListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/factura/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturacliente_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado."""
        self.create_user(['list_factura'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/factura/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturacliente_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/factura/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta listar."""
        response = self.client.get('/factura/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_length_in_template(self):
        """Verifica cantidad de instancias en el template listado."""
        instance = FacturaClienteFactory.create()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/factura/')
        self.assertQuerysetEqual(response.context['object_list'], [instance], transform=lambda x: x)

    def test_last_created_in_template(self):
        """Verifica cantidad de instancias creadas en la semana."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/factura/')
        self.assertEqual(response.context['last_created'], Factura.objects.count())

    def test_list_empty(self):
        """Verifica un listado vacío cuando no hay instancias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/factura/')
        self.assertContains(response, 'Sin resultados')


class FacturaClienteCreateViewTest(BaseTestCase):
    """Tests sobre la vista de crear."""

    def setUp(self):
        self.data = FacturaClienteFactoryData().build()

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/factura/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturacliente_form.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['add_factura'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/factura/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturacliente_form.html')

    @prevent_request_warnings
    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/factura/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear."""
        response = self.client.get('/factura/agregar/')
        self.assertEqual(response.status_code, 302)

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que un usuario sin permisos no pueda realizar un post."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/factura/agregar/')
        self.assertEqual(response.status_code, 403)

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta realizar un post."""
        response = self.client.post('/factura/agregar/')
        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        user = self.create_superuser()
        self.client.login(username='user', password='user12345')
        form = FacturaForm(data=self.data, user=user)
        self.assertTrue(form.is_valid())

    def test_form_user_without_permissions_cant_change_value(self):
        """
        Valida que un usuario sin permisos no pueda cambiar los valores de
        numero de factura, moneda, neto, iva y total.
        """
        user = self.create_user()
        self.client.login(username='user', password='user12345')
        self.data.update({'moneda': 'D'})  # cambia el valor por defecto
        form = FacturaForm(data=self.data, user=user)
        self.assertHasProps(form.errors, ['numero', 'moneda', 'iva', 'neto', 'total'])
        self.assertHasErrorDetail(form.errors.get('numero'), 'No tienes permisos para cambiar este campo.')
        self.assertHasErrorDetail(form.errors.get('moneda'), 'No tienes permisos para cambiar este campo.')
        self.assertHasErrorDetail(form.errors.get('iva'), 'No tienes permisos para cambiar este campo.')
        self.assertHasErrorDetail(form.errors.get('neto'), 'No tienes permisos para cambiar este campo.')
        self.assertHasErrorDetail(form.errors.get('total'), 'No tienes permisos para cambiar este campo.')

    def test_form_user_with_permission_change_values(self):
        """
        Valida que un usuario con permisos pueda cambiar los valores de
        numero de factura, moneda, neto, iva y total.
        """
        user = self.create_user(
            [
                'change_nro_factura',
                'change_moneda_factura',
                'change_neto_factura',
                'change_iva_factura',
                'change_total_factura',
            ]
        )
        self.client.login(username='user', password='user12345')
        form = FacturaForm(data=self.data, user=user)
        self.assertTrue(form.is_valid())

    def test_form_fields_required(self):
        """Valida los campos requeridos."""
        user = self.create_superuser()
        form = FacturaForm(data={}, user=user)
        required_fields = ['fecha', 'numero', 'tipo', 'cliente', 'moneda', 'neto', 'iva', 'total', 'porcentaje_fondo']
        self.assertHasProps(form.errors, required_fields)

    def test_form_total_zero(self):
        """Valida el total de la factura no sea cero."""
        user = self.create_superuser()
        self.data['total'] = 0.0
        form = FacturaForm(data=self.data, user=user)
        self.assertHasErrorDetail(form.errors.get('total'), 'El total no puede ser igual a 0.')

    def test_form_total_invalid(self):
        """Valida que el total corresponda a la suma del porcentaje sobre el valor neto."""
        user = self.create_superuser()
        self.data['total'] = self.data.get('total') + 1
        form = FacturaForm(data=self.data, user=user)
        self.assertHasErrorDetail(form.errors.get('total'), 'El total ingresado no es el correcto.')

    def test_form_fondo_create(self):
        """Valida que se crea un fondo al generar una factura."""
        user = self.create_superuser()
        form = FacturaForm(data=self.data, user=user)
        form.is_valid()
        instance = form.save()
        fondo = Fondo.objects.filter(
            factura=instance,
            moneda=instance.moneda,
            monto=instance.porcentaje_fondo_monto,
            monto_disponible=instance.porcentaje_fondo_monto,
            disponible=instance.cobrado,
        )
        self.assertTrue(fondo.exists())


class FacturaClienteDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = FacturaClienteFactory.create()

    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/factura/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturacliente_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['view_factura'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/factura/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturacliente_detail.html')

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/factura/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar."""
        response = self.client.get(f'/factura/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class FacturaClienteUpdateViewTest(BaseTestCase):
    """Test sobre la vista de editar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = FacturaClienteFactory.create()
        self.data = FacturaClienteFactoryData().build()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/factura/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturacliente_form.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar."""
        self.create_user(['change_factura'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/factura/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturacliente_form.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/factura/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.get(f'/factura/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post(f'/factura/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.post(f'/factura/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_form_user_without_permissions_cant_change_value(self):
        """
        Valida que un usuario sin permisos no pueda cambiar los valores de
        numero de factura, moneda, neto, iva y total.
        """
        user = self.create_user()
        self.client.login(username='user', password='user12345')
        data = {  # Modifica valores de la instancia
            'numero': self.instance.numero + 1,
            'moneda': 'P' if self.instance.moneda == 'D' else 'D',
            'iva': self.instance.iva + 1,
            'neto': self.instance.neto + 1,
            'total': self.instance.total + 1,
        }
        form = FacturaForm(instance=self.instance, data=data, user=user)
        self.assertHasProps(form.errors, ['numero', 'iva', 'neto', 'total'])
        self.assertHasErrorDetail(form.errors.get('numero'), 'No tienes permisos para cambiar este campo.')
        self.assertHasErrorDetail(form.errors.get('moneda'), 'No tienes permisos para cambiar este campo.')
        self.assertHasErrorDetail(form.errors.get('iva'), 'No tienes permisos para cambiar este campo.')
        self.assertHasErrorDetail(form.errors.get('neto'), 'No tienes permisos para cambiar este campo.')
        self.assertHasErrorDetail(form.errors.get('total'), 'No tienes permisos para cambiar este campo.')

    def test_form_user_with_permission_change_values(self):
        """
        Valida que un usuario con permisos pueda cambiar los valores de
        numero de factura, moneda, neto, iva y total.
        """
        user = self.create_user(
            [
                'change_nro_factura',
                'change_moneda_factura',
                'change_neto_factura',
                'change_iva_factura',
                'change_total_factura',
            ]
        )
        self.client.login(username='user', password='user12345')
        form = FacturaForm(data=self.data, instance=self.instance, user=user)
        self.assertTrue(form.is_valid())

    def test_form_fondo_update(self):
        """Valida que se crea un fondo al generar una factura."""
        user = self.create_superuser()
        # crea
        form = FacturaForm(data=self.data, user=user)
        form.is_valid()
        instance = form.save()
        # Edita
        form = FacturaForm(data=self.data, instance=instance, user=user)
        form.is_valid()
        instance = form.save()
        fondo = Fondo.objects.filter(
            factura=instance,
            moneda=instance.moneda,
            monto=instance.porcentaje_fondo_monto,
            monto_disponible=instance.porcentaje_fondo_monto,
            disponible=instance.cobrado,
        )
        self.assertTrue(fondo.exists())


class FacturaClienteDeleteViewTest(BaseTestCase):
    """Test sobre la vista de eliminar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = FacturaClienteFactory.create()

    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/factura/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturacliente_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar."""
        self.create_user(['delete_factura'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/factura/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturacliente_confirm_delete.html')

    @prevent_request_warnings
    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/factura/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.get(f'/factura/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_detroy_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.delete(f'/factura/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detroy_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.delete(f'/factura/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')
