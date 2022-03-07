"""Costos test."""

# Django
from django.core.management import call_command
from faker import Faker

from sistemita.core.constants import ZERO_DECIMAL

# Sistemita
from sistemita.expense.forms import CostoForm
from sistemita.expense.models import Fondo
from sistemita.expense.tests.factories import (
    CostoFactory,
    CostoFactoryData,
    FondoFactory,
)
from sistemita.utils.tests import (
    BaseTestCase,
    prevent_request_warnings,
    rand_range,
)

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class CostoModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = CostoFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        costo = self.instance
        self.assertEqual(str(costo), f'{costo.fecha} | {costo.monto}')


class CostoListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/costo/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='expense/costo_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado."""
        self.create_user(['list_costo'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/costo/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='expense/costo_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/costo/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta listar."""
        response = self.client.get('/costo/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_length_in_template(self):
        """Verifica cantidad de instancias en el template listado."""
        instance = CostoFactory.create()
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/costo/')
        self.assertQuerysetEqual(response.context['object_list'], [instance], transform=lambda x: x)

    def test_list_empty(self):
        """Verifica un listado vacío cuando no hay instancias."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/costo/')
        self.assertContains(response, 'Sin resultados')


class CostoCreateViewTest(BaseTestCase):
    """Tests sobre la vista de crear."""

    def setUp(self):
        self.data_create = CostoFactoryData().create()

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear costos."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/costo/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='expense/costo_form.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar costos."""
        self.create_user(['add_costo'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/costo/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='expense/costo_form.html')

    @prevent_request_warnings
    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear costos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/costo/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear costos."""
        response = self.client.get('/costo/agregar/')
        self.assertEqual(response.status_code, 302)

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que un usuario sin permisos no pueda realizar un post."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/costo/agregar/')
        self.assertEqual(response.status_code, 403)

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta realizar un post."""
        response = self.client.post('/costo/agregar/')
        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        form = CostoForm(data=self.data_create)
        form.is_valid()
        self.assertTrue(form.is_valid())

    def test_form_fields_required(self):
        """Valida formulario con datos correctos."""
        form = CostoForm(data={})
        form.is_valid()
        self.assertHasProps(
            form.errors,
            [
                'fecha',
                'descripcion',
                'fondo',
                'moneda',
                'monto',
            ],
        )

    def test_validate_same_moneda(self):
        """Valida que el fondo y el costo sean de la misma moneda."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        data['moneda'] = 'P' if data.get('moneda') == 'D' else 'D'
        form = CostoForm(data=data)
        form.is_valid()
        self.assertHasErrorDetail(form.errors.get('moneda'), 'La moneda debe ser igual a la moneda de la factura.')

    def test_validate_monto_greater_that_fondo_monto_disponible(self):
        """Valida que el monto del costo no sea mayor al monto disponible del fondo."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        data = self.data_create
        fondo = Fondo.objects.get(pk=data.get('fondo'))
        data['monto'] = fondo.monto_disponible + 1
        form = CostoForm(data=data)
        form.is_valid()
        self.assertHasErrorDetail(form.errors.get('monto'), 'El monto debe ser menor o igual al monto disponible.')

    def test_validate_fondo_monto_disponible(self):
        """
        Valida que el monto disponible del fondo quede en cero en caso de que el monto del costo
        sea del mismo valor.
        """
        form = CostoForm(data=self.data_create)
        form.is_valid()
        instance = form.save()
        self.assertEqual(instance.fondo.monto_disponible, ZERO_DECIMAL)

    def test_validate_fondo_disponible(self):
        """Valida que el fondo ya no esté disponible en caso de que el monto del costo sea del mismo valor."""
        form = CostoForm(data=self.data_create)
        form.is_valid()
        instance = form.save()
        self.assertFalse(instance.fondo.disponible)


class CostoDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = CostoFactory.create()

    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar costos."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/costo/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='expense/costo_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar costos."""
        self.create_user(['view_costo'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/costo/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='expense/costo_detail.html')

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar costos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/costo/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar costos."""
        response = self.client.get(f'/costo/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class CostoUpdateViewTest(BaseTestCase):
    """Test sobre la vista de editar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = CostoFactory.create()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar costos."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/costo/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='expense/costo_form.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar costos."""
        self.create_user(['change_costo'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/costo/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='expense/costo_form.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar costos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/costo/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar costos."""
        response = self.client.get(f'/costo/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post(f'/costo/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.post(f'/costo/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_update_validate_amount_fondos(self):
        """Al aplicar costos, el monto disponible del fondo debe ir restandose."""
        fondo = FondoFactory.create()
        subtract = rand_range(1, (round(fondo.monto_disponible) - 1))
        monto_disponible = fondo.monto_disponible - subtract

        # Crea 2 costos que hacen que el fondo quede con un monto disponible de 1
        CostoFactory.create(fondo=fondo, monto=monto_disponible)
        costo_2 = CostoFactory.create(fondo=fondo, monto=subtract - 1)
        fondo.monto_disponible = 1
        fondo.save()

        monto = costo_2.monto + 1
        data = {
            'fecha': costo_2.fecha,
            'descripcion': costo_2.descripcion,
            'fondo': costo_2.fondo,
            'moneda': costo_2.moneda,
            'monto': monto,
        }
        form = CostoForm(instance=costo_2, data=data)
        form.is_valid()
        instance = form.save()
        self.assertEqual(instance.fondo.monto_disponible, ZERO_DECIMAL)

    def test_update_validate_validate_amount_fondos(self):
        """Valida que si hay más de un costo asociado a un fondo, la suma de los costos no sea mayor a la del fondo."""
        fondo = FondoFactory.create()
        monto_costo_1 = round(fondo.monto_disponible / 2, 2)
        CostoFactory.create(fondo=fondo, monto=monto_costo_1)
        costo_2 = CostoFactory.create(fondo=fondo, monto=monto_costo_1)
        data = {
            'fecha': costo_2.fecha,
            'descripcion': costo_2.descripcion,
            'fondo': costo_2.fondo,
            'moneda': costo_2.moneda,
            'monto': monto_costo_1 + 1,
        }
        form = CostoForm(instance=costo_2, data=data)
        form.is_valid()
        self.assertHasErrorDetail(
            form.errors.get('monto'), 'La suma de costos para este fondo supera el monto del fondo.'
        )

    def test_update_costo_validate_monto_disponible(self):
        """Valida que si el monto se lo cambia por un valor menos, el monto disponible del fondo debe incrementarse."""
        self.instance.fondo.monto_disponible = 0
        self.instance.fondo.save()
        data = {
            'fecha': self.instance.fecha,
            'descripcion': self.instance.descripcion,
            'fondo': self.instance.fondo,
            'moneda': self.instance.moneda,
            'monto': self.instance.monto - 1,
        }
        form = CostoForm(instance=self.instance, data=data)
        form.is_valid()
        instance = form.save()
        self.assertEqual(instance.fondo.monto_disponible, 1)

    def test_update_costo_validate_fondo_disponible(self):
        """Valida que si el monto se lo cambia por un valor menos, el fondo pasa a estar disponible."""
        self.instance.fondo.monto_disponible = 0
        self.instance.fondo.save()
        monto = self.instance.monto - 1
        data = {
            'fecha': self.instance.fecha,
            'descripcion': self.instance.descripcion,
            'fondo': self.instance.fondo,
            'moneda': self.instance.moneda,
            'monto': monto,
        }
        form = CostoForm(instance=self.instance, data=data)
        form.is_valid()
        instance = form.save()
        self.assertTrue(instance.fondo.disponible)

    def test_update_fondo(self):
        """Valida que al cambiar el fondo el monto del anterior de fondo sea restablecido."""
        fondo = FondoFactory.create()
        fondo_previous = self.instance.fondo
        data = {
            'fecha': self.instance.fecha,
            'descripcion': self.instance.descripcion,
            'fondo': fondo.pk,
            'moneda': self.instance.moneda,
            'monto': self.instance.monto,
        }
        CostoForm(instance=self.instance, data=data)
        fondo_previous.refresh_from_db()
        self.assertTrue(fondo_previous.disponible)
        self.assertEqual(fondo_previous.monto, fondo_previous.monto_disponible)


class CostoDeleteViewTest(BaseTestCase):
    """Test sobre la vista de eliminar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = CostoFactory.create()

    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar costos."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/costo/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='expense/costo_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar costos."""
        self.create_user(['delete_costo'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/costo/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='expense/costo_confirm_delete.html')

    @prevent_request_warnings
    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar costos."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/costo/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar costos."""
        response = self.client.get(f'/costo/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_detroy_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.delete(f'/costo/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detroy_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.delete(f'/costo/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_destroy_factura_restore(self):
        """Verifica que el fondo sea restablecido al ser eliminado el costo."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        fondo = self.instance.fondo
        response = self.client.delete(f'/costo/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(fondo.monto, fondo.monto_disponible)
        self.assertTrue(fondo.disponible)
