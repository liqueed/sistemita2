from django.test import TestCase
from .conciliador_automatico_de_movimientos_bancarios import *
from .models import MovimientoBancario

class TestsConciliadorAutomatico(TestCase):

    def test_detecta_correctamente_movimiento_pago_de_cliente(self):
        movimiento_pago_de_cliente = MovimientoBancario(codigo_operativo='2377',\
            concepto='Pago Proveedores Interbanking Exte  - O.s.d.e. 30546741253 03 6968308 ')
        lector = LectorDeMovimientoAbstracto.detectarTipoCorrectoDeMovimiento(movimiento_pago_de_cliente)
        assert (lector == LectorDeMovimientoDePagoDeCliente)