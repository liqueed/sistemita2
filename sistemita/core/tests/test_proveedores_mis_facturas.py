"""Factura de Proveedores tests."""

# Django
from django.core.management import call_command
from faker import Faker

# Sistemita
from sistemita.core.models import FacturaProveedor
from sistemita.core.tests.factories import (
    FacturaProveedorFactory,
    ProveedorFactory,
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


class ProveedorMisFacturasListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/factura-proveedor/mis-facturas/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedor_misfacturas.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado."""
        self.create_user(['view_mis_facturasproveedor'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/factura-proveedor/mis-facturas/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedor_misfacturas.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/factura-proveedor/mis-facturas/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta listar."""
        response = self.client.get('/factura-proveedor/mis-facturas/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_list_mis_facturas_in_template(self):
        """
        Verifica cantidad de instancias en el template listado.
        El proveedor debe tener su usuario, para ello debe coincidir el email entre ambas instancias.
        """
        email = 'user@sistem.io'
        self.create_user(['view_mis_facturasproveedor'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        proveedor = ProveedorFactory.create(correo=email)
        instance = FacturaProveedorFactory.create(proveedor=proveedor)
        response = self.client.get('/factura-proveedor/mis-facturas/')
        self.assertQuerysetEqual(response.context['object_list'], [instance], transform=lambda x: x)

    def test_list_facturas_user_in_template(self):
        """
        Verifica que solo aparezcan las facturas del usuario que hace la petición.
        """
        email = 'user@sistem.io'
        self.create_user(['view_mis_facturasproveedor'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        proveedor = ProveedorFactory.create(correo=email)
        limit = rand_range(1, 5)
        FacturaProveedorFactory.create_batch(proveedor=proveedor, size=limit)
        # Otro usuario/proveedor crea facturas
        proveedor_2 = ProveedorFactory.create()
        FacturaProveedorFactory.create_batch(proveedor=proveedor_2, size=limit)
        response = self.client.get('/factura-proveedor/mis-facturas/')
        results = 0
        for item in response.context['object_list']:
            results += FacturaProveedor.objects.filter(pk=item.pk, proveedor=proveedor).exists()
        self.assertEqual(limit, results)

    def test_list_empty(self):
        """Verifica un listado vacío cuando no hay instancias."""
        email = 'user@sistem.io'
        self.create_user(['view_mis_facturasproveedor'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        ProveedorFactory.create(correo=email)
        response = self.client.get('/factura-proveedor/mis-facturas/')
        self.assertContains(response, 'Sin resultados')
        self.assertEqual(response.status_code, 200)


class ProveedorMisFacturaDetailViewTest(BaseTestCase):
    """Test sobre la vista de detalle."""

    def setUp(self):
        self.instance = FacturaProveedorFactory.create()

    @prevent_request_warnings
    def test_detail_with_superuser(self):
        """Verifica que el usuario admin no puede acceder a detallar otras facturas."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get(f'/factura-proveedor/mis-facturas/{self.instance.pk}/')
        self.assertEqual(response.status_code, 404)

    @prevent_request_warnings
    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos no puede acceder a detallar otras facturas en este módulo."""
        self.create_user(['view_mis_facturasproveedor'])
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/factura-proveedor/mis-facturas/{self.instance.pk}/')
        self.assertEqual(response.status_code, 404)

    @prevent_request_warnings
    def test_detail_with_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder a detallar."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get(f'/factura-proveedor/mis-facturas/{self.instance.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_detail_with_user_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta detallar."""
        response = self.client.get(f'/factura-proveedor/mis-facturas/{self.instance.pk}/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_detail_mis_facturas_in_template(self):
        """Verifica un usuario/proveedor con permisos pueda detallar sus propias facturas."""
        email = 'user@sistem.io'
        self.create_user(['view_mis_facturasproveedor'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        proveedor = ProveedorFactory.create(correo=email)
        instance = FacturaProveedorFactory.create(proveedor=proveedor)
        response = self.client.get(f'/factura-proveedor/mis-facturas/{instance.pk}/')
        self.assertTemplateUsed(response, template_name='core/facturaproveedor_user_detail.html')
        self.assertEqual(response.status_code, 200)
