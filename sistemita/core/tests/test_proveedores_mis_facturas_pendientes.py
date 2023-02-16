"""Factura pendientes de Proveedores tests."""

# Django
from django.core.management import call_command

# Sistemita
from sistemita.core.tests.factories import (
    FacturaDistribuidaProveedorFactory,
    ProveedorFactory,
)
from sistemita.utils.tests import BaseTestCase, prevent_request_warnings


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class FacturaProveedorByUserPendientesListViewTestCase(BaseTestCase):
    """Test sobre la vista de factura pendientes de proveedores."""

    @prevent_request_warnings
    def test_add_with_superuser(self):
        """Verifica que el usuario admin puede acceder a crear."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/factura-proveedor/mis-facturas-pendientes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedor_misfacturas_pendientes.html')

    @prevent_request_warnings
    def test_detail_with_user_in_group(self):
        """Verifica que el usuario con permisos no puede acceder a detallar otras facturas en este módulo."""
        self.create_user(['view_mis_facturasproveedor_pendientes'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/factura-proveedor/mis-facturas-pendientes/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedor_misfacturas_pendientes.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/factura-proveedor/mis-facturas-pendientes/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta listar."""
        response = self.client.get('/factura-proveedor/mis-facturas-pendientes/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')

    def test_list_mis_facturas_pendientes_in_template(self):
        """
        Verifica cantidad de instancias en el template listado.
        El proveedor debe tener su usuario, para ello debe coincidir el email entre ambas instancias.
        """
        email = 'user@sistem.io'
        self.create_user(['view_mis_facturasproveedor_pendientes'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        proveedor = ProveedorFactory.create(correo=email)
        instance = FacturaDistribuidaProveedorFactory.create(proveedor=proveedor)
        response = self.client.get('/factura-proveedor/mis-facturas-pendientes/')
        self.assertQuerysetEqual(response.context['object_list'], [instance], transform=lambda x: x)

    def test_list_empty(self):
        """Verifica un listado vacío cuando no hay instancias."""
        email = 'user@sistem.io'
        self.create_user(['view_mis_facturasproveedor_pendientes'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        ProveedorFactory.create(correo=email)
        response = self.client.get('/factura-proveedor/mis-facturas-pendientes/')
        self.assertContains(response, 'No hay facturas pendientes')
        self.assertEqual(response.status_code, 200)
