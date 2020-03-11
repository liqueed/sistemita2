from django.test import TestCase, LiveServerTestCase
from django.urls import resolve
from .conciliador_automatico.conciliador_automatico_de_movimientos_bancarios import ConciliadorAutomaticoDeMovimientosBancarios, LectorDeMovimientoAbstracto
from .conciliador_automatico.lector_de_movimiento_de_pago_a_consultor import *
from .conciliador_automatico.lector_de_movimiento_de_pago_de_cliente import *
from .models import MovimientoBancario, Consultor, FacturadorDeConsultor
from .views import importar_resumen_bancario
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class TestsConciliadorAutomatico(TestCase):

    def test_detecta_correctamente_movimiento_pago_de_cliente(self):
        movimiento_pago_de_cliente = MovimientoBancario(codigo_operativo='2377',\
            concepto='Pago Proveedores Interbanking Exte  - O.s.d.e. 30546741253 03 6968308 ')
        lector = LectorDeMovimientoAbstracto.detectarTipoCorrectoDeMovimiento(movimiento_pago_de_cliente)
        assert (lector == LectorDeMovimientoDePagoDeCliente)

    def test_detecta_correctamente_movimiento_pago_a_consultor(self):
        consultor = Consultor(nombre='David')
        consultor.save()
        facturador = FacturadorDeConsultor(consultor=consultor, cuit='279465743627', cbu='1500035000008161431046')
        facturador.save()
        movimiento_pago_a_consultor = MovimientoBancario(codigo_operativo='0824',\
            concepto='Pago Cci 24hs Gravada Interbanking  - A Cbu 1500035000008161431046 ')
        lector = LectorDeMovimientoAbstracto.detectarTipoCorrectoDeMovimiento(movimiento_pago_a_consultor)
        assert (lector == LectorDeMovimientoDePagoAConsultor)

class TestsUI(LiveServerTestCase):
    
    def setUp(self):  
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(options=options)

    def tearDown(self):  
        self.browser.quit()

    def test_resuelve_url_importacion_resumen_bancario(self):
        found = resolve('/importar_resumen_bancario/')
        self.assertEqual(found.func, importar_resumen_bancario)

    def test_importar_resumen_bancario(self):
        
        self.browser.get('http://localhost:8000/importar_resument_bancario')

        assert 'Importar resumen bancario' in self.browser.title