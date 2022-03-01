"""Factura de Proveedores tests."""

# Django
from django.core.management import call_command
from faker import Faker

# Sistemita
from sistemita.utils.tests import BaseTestCase, prevent_request_warnings

fake = Faker('es_ES')


def setUpModule():
    """Agrega permisos a utilizar por los test."""
    call_command('add_permissions', verbosity=0)


class FacturaProveedorReporteListViewTest(BaseTestCase):
    """Test sobre vista de listado."""

    def test_list_with_superuser(self):
        """Verifica que el usuario admin puede acceder al listado."""
        self.create_superuser()
        self.client.login(username='admin', password='admin123')  # login super user
        response = self.client.get('/factura-proveedor/reporte-ventas/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedor_report_list.html')

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al listado."""
        self.create_user(['view_report_sales_facturaproveedor'])
        self.client.login(username='user', password='user12345')
        response = self.client.get('/factura-proveedor/reporte-ventas/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/facturaproveedor_report_list.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al listado."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/factura-proveedor/reporte-ventas/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_with_anonymous(self):
        """Verifica que redirige al login al usuario sin acceso intenta listar."""
        response = self.client.get('/factura-proveedor/reporte-ventas/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/')
