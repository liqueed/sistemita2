"""Tests de las vistas de usuarios."""

# Django
from django.core.management import call_command
from faker import Faker

from sistemita.authorization.forms import (
    PasswordResetForm,
    UserCreateForm,
    UserUpdateForm,
)

# Sistemita
from sistemita.authorization.models import User
from sistemita.authorization.tests.factories import (
    UserFactory,
    UserFactoryData,
)
from sistemita.utils.tests import BaseTestCase, prevent_request_warnings

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('permissions_translation', verbosity=0)
    call_command('add_permissions', verbosity=0)


class UserModelTest(BaseTestCase):
    """Test sobre el modelo."""

    def setUp(self):
        self.instance = UserFactory.build()

    def test_string_representation(self):
        """Representación legible del modelo."""
        user = self.instance
        self.assertEqual(str(user), f'{user.username}')

    def test_full_name(self):
        """Devuelve el nombre completo del usuario."""
        user = self.instance
        self.assertEqual(str(user.full_name), f'{self.instance.last_name} {self.instance.first_name}')


class UserListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def setUp(self):
        self.instance = UserFactory.create()

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/usuario/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/user_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado."""
        self.create_user(['list_user'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/usuario/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/user_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/usuario/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta listar."""
        response = self.client.get('/usuario/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_length_in_template(self):
        """Verifica cantidad de instancias en el template listado."""
        super_user = self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/usuario/')
        self.assertQuerysetEqual(response.context['object_list'], [super_user, self.instance], transform=lambda x: x)

    def test_last_created_in_template(self):
        """Verifica cantidad de instancias creadas en la semana."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/usuario/')
        self.assertEqual(response.context['last_created'], User.objects.count())


class UserCreateViewTest(BaseTestCase):
    """Tests sobre la vista de crear."""

    def setUp(self):
        self.data = UserFactoryData().build()

    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/usuario/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/user_form.html')

    def test_add_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['add_user'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/usuario/agregar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/user_form.html')

    @prevent_request_warnings
    def test_add_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a crear."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/usuario/agregar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_add_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta crear."""
        response = self.client.get('/usuario/agregar/')
        self.assertEqual(response.status_code, 302)

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que un usuario sin permisos no pueda realizar un post."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post('/usuario/agregar/')
        self.assertEqual(response.status_code, 403)

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta realizar un post."""
        response = self.client.post('/usuario/agregar/')
        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        form = UserCreateForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_form_fields_required(self):
        """Valida los campos requeridos."""
        form = UserCreateForm(data={})
        required_fields = ['first_name', 'last_name', 'username', 'email', 'password', 'password_confirmation']
        self.assertHasProps(form.errors, required_fields)

    def test_username_unique(self):
        """Verifica si el username ya está registrado."""
        form = UserCreateForm(data=self.data)
        form.is_valid()
        form.save()
        user_2 = UserFactoryData().build()
        user_2['username'] = self.data.get('username')
        form_2 = UserCreateForm(data=user_2)
        self.assertHasErrorDetail(form_2.errors['username'], 'El username ya está registrado.')

    def test_email_unique(self):
        """Verifica si el email ya está registrado."""
        form = UserCreateForm(data=self.data)
        form.is_valid()
        form.save()
        user_2 = UserFactoryData().build()
        user_2['email'] = self.data.get('email')
        form_2 = UserCreateForm(data=user_2)
        self.assertHasErrorDetail(form_2.errors['email'], 'El email ya está registrado.')

    def test_form_email_invalid(self):
        """Valida el email."""
        self.data['email'] = 'wrong@mail'
        form = UserCreateForm(data=self.data)
        self.assertHasProps(
            form.errors,
            [
                'email',
            ],
        )

    def test_password_not_match_invalid(self):
        """Valida que el password y la confirmación de password coincidan."""
        self.data['password_confirmation'] = '123456'
        form = UserCreateForm(data=self.data)
        self.assertHasErrorDetail(form.errors['password_confirmation'], 'Las contraseñas no coinciden.')


class UserDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = UserFactory.create()

    def test_detail_with_superuser(self):
        """Verifica que el usuario admin puede acceder a detallar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/usuario/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/user_detail.html')

    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a agregar."""
        self.create_user(['view_user'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/usuario/{self.instance.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/user_detail.html')

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/usuario/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar."""
        response = self.client.get(f'/usuario/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')


class UserUpdateViewTest(BaseTestCase):
    """Test sobre la vista de editar."""

    def setUp(self):
        """Creación de instancia."""
        self.data = UserFactoryData().build()
        self.instance = UserFactory.create()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/usuario/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/user_form.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar."""
        self.create_user(['change_user'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/usuario/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/user_form.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/usuario/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.get(f'/usuario/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post(f'/usuario/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.post(f'/usuario/{self.instance.pk}/editar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        data = self.data
        data.pop('password')
        data.pop('password_confirmation')
        form = UserUpdateForm(data=data)
        self.assertTrue(form.is_valid())

    def test_form_fields_required(self):
        """Valida los campos requeridos."""
        form = UserUpdateForm(data={})
        required_fields = ['first_name', 'last_name', 'username', 'email']
        self.assertHasProps(form.errors, required_fields)

    def test_username_unique(self):
        """Verifica si el username ya está registrado."""
        form = UserCreateForm(data=self.data)
        form.is_valid()
        form.save()
        user_2 = UserFactoryData().build()
        user_2['username'] = self.data.get('username')
        form_2 = UserUpdateForm(data=user_2)
        self.assertHasErrorDetail(form_2.errors['username'], 'Ya existe un usuario con ese nombre.')

    def test_email_unique(self):
        """Verifica si el email ya está registrado."""
        form = UserCreateForm(data=self.data)
        form.is_valid()
        form.save()
        user_2 = UserFactoryData().build()
        user_2['email'] = self.data.get('email')
        form_2 = UserUpdateForm(data=user_2)
        self.assertHasErrorDetail(form_2.errors['email'], 'Este email ya está en uso.')

    def test_form_email_invalid(self):
        """Valida el email."""
        self.data['email'] = 'wrong@mail'
        form = UserUpdateForm(data=self.data)
        self.assertHasProps(
            form.errors,
            [
                'email',
            ],
        )


class PasswordChangeFormViewTest(BaseTestCase):
    """PasswordChangeForm Test."""

    def setUp(self):
        """Creación de instancia."""
        self.data = UserFactoryData().build()
        self.instance = UserFactory.create()

    def test_update_with_superuser(self):
        """Verifica que el usuario admin puede acceder a editar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/usuario/{self.instance.pk}/password/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/password_change.html')

    def test_update_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a editar."""
        self.create_user(['change_user'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/usuario/{self.instance.pk}/password/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/password_change.html')

    @prevent_request_warnings
    def test_update_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/usuario/{self.instance.pk}/password/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_update_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.get(f'/usuario/{self.instance.pk}/password/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_post_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a editar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.post(f'/usuario/{self.instance.pk}/password/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_post_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta editar."""
        response = self.client.post(f'/usuario/{self.instance.pk}/password/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_form_valid(self):
        """Valida formulario con datos correctos."""
        data = {
            'new_password1': self.data.get('password'),
            'new_password2': self.data.get('password_confirmation'),
        }
        form = PasswordResetForm(user=self.instance, data=data)
        self.assertTrue(form.is_valid())

    def test_password_common_value(self):
        """Valida que la contraseña sea fuerte."""
        data = {
            'new_password1': '123456',
            'new_password2': '123456',
        }
        form = PasswordResetForm(user=self.instance, data=data)
        self.assertHasErrorDetail([form.errors['new_password2'][1]], 'La contraseña tiene un valor demasiado común.')

    def test_password_not_match(self):
        """Valida formulario con datos correctos."""
        data = {
            'new_password1': self.data.get('password'),
            'new_password2': '123456',
        }
        form = PasswordResetForm(user=self.instance, data=data)
        self.assertHasErrorDetail(form.errors['new_password2'], 'Los dos campos de contraseñas no coinciden entre si.')


class UserDeleteViewTest(BaseTestCase):
    """Test sobre la vista de eliminar."""

    def setUp(self):
        """Creación de instancia."""
        self.instance = UserFactory.create()

    def test_delete_with_superuser(self):
        """Verifica que el usuario admin puede acceder a eliminar."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/usuario/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/user_confirm_delete.html')

    def test_delete_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder a eliminar."""
        self.create_user(['delete_user'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/usuario/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='authorization/user_confirm_delete.html')

    @prevent_request_warnings
    def test_delete_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/usuario/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_delete_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.get(f'/usuario/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    @prevent_request_warnings
    def test_detroy_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a eliminar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.delete(f'/usuario/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detroy_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta eliminar."""
        response = self.client.delete(f'/usuario/{self.instance.pk}/eliminar/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')
