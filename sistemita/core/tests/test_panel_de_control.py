"""Test panel de control."""

# Django
from django.core.management import call_command
from faker import Faker

# Sistemita
from sistemita.core.tests.factories import (
    ContratoFactory,
    FacturaClienteFactory,
    FacturaDistribuidaFactory,
    FacturaDistribuidaProveedorFactory,
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


class PanelDeControlTemplateViewTest(BaseTestCase):
    """Test sobre vista del panel."""

    def test_list_with_user_in_group(self):
        """Verifica que el usuario con permisos puede acceder al panel de control."""
        email = 'user@sistem.io'
        self.create_user(['view_paneldecontrol'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        ProveedorFactory.create(correo=email)
        response = self.client.get('/paneldecontrol/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/panel_de_control.html')

    @prevent_request_warnings
    def test_list_user_no_permissions(self):
        """Verifica que el usuario sin permisos no pueda acceder al panel de control."""
        self.create_user()
        self.client.login(username='user', password='user12345')
        response = self.client.get('/paneldecontrol/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, template_name='403.html')

    def test_list_contratos(self):
        """Verifica que en panel haya un listado de contratos."""
        email = 'user@sistem.io'
        self.create_user(['view_paneldecontrol'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        proveedor = ProveedorFactory.create(correo=email)

        length = rand_range(2, 5)
        for _ in range(0, length):
            ContratoFactory.create(proveedores=[proveedor])
        response = self.client.get('/paneldecontrol/')
        self.assertEqual(len(response.context['contratos']), length)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/panel_de_control.html')

    def test_list_card_enviada(self):
        """Verifica que en panel haya una tarjeta en estado enviada."""
        email = 'user@sistem.io'
        self.create_user(['view_paneldecontrol'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        proveedor = ProveedorFactory.create(correo=email)
        factura = FacturaClienteFactory.create(proveedores=[proveedor], cobrado=False)
        FacturaDistribuidaFactory.create(factura=factura)
        response = self.client.get('/paneldecontrol/')
        self.assertEqual(response.context['groups'][0][0].status, 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/panel_de_control.html')

    def test_list_card_cobrada(self):
        """Verifica que en panel haya una tarjeta en estado cobrada."""
        email = 'user@sistem.io'
        self.create_user(['view_paneldecontrol'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        proveedor = ProveedorFactory.create(correo=email)
        factura = FacturaClienteFactory.create(proveedores=[proveedor], cobrado=True)
        factura_distribuida = FacturaDistribuidaFactory.create(factura=factura, distribuida=True)
        factura_proveedor = FacturaProveedorFactory(proveedor=proveedor, factura=factura, cobrado=False)
        FacturaDistribuidaProveedorFactory.create(
            factura_distribucion=factura_distribuida, proveedor=proveedor, factura_proveedor=factura_proveedor
        )
        response = self.client.get('/paneldecontrol/')
        factura.refresh_from_db()
        self.assertEqual(response.context['groups'][0][1].status, 2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/panel_de_control.html')

    def test_list_card_demorada(self):
        """Verifica que en panel haya una tarjeta en estado demorada."""
        email = 'user@sistem.io'
        self.create_user(['view_paneldecontrol'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        proveedor = ProveedorFactory.create(correo=email)
        factura = FacturaClienteFactory.create(proveedores=[proveedor], cobrado=False)
        factura_distribuida = FacturaDistribuidaFactory.create(factura=factura, distribuida=True)
        factura_proveedor = FacturaProveedorFactory(proveedor=proveedor, factura=factura)
        FacturaDistribuidaProveedorFactory.create(
            factura_distribucion=factura_distribuida, proveedor=proveedor, factura_proveedor=factura_proveedor
        )
        factura.refresh_from_db()
        response = self.client.get('/paneldecontrol/')
        self.assertEqual(response.context['groups'][0][2].status, 3)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/panel_de_control.html')

    def test_list_card_lista(self):
        """Verifica que en panel haya una tarjeta en estado lista :)."""
        email = 'user@sistem.io'
        self.create_user(['view_paneldecontrol'], email=email)
        self.client.login(username='user', password='user12345', email=email)
        proveedor = ProveedorFactory.create(correo=email)
        factura = FacturaClienteFactory.create(proveedores=[proveedor], cobrado=True)
        factura_distribuida = FacturaDistribuidaFactory.create(factura=factura, distribuida=True)
        factura_proveedor = FacturaProveedorFactory(proveedor=proveedor, factura=factura, cobrado=True)
        FacturaDistribuidaProveedorFactory.create(
            factura_distribucion=factura_distribuida, proveedor=proveedor, factura_proveedor=factura_proveedor
        )
        factura.refresh_from_db()
        response = self.client.get('/paneldecontrol/')
        self.assertEqual(response.context['groups'][0][3].status, 4)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='core/panel_de_control.html')
