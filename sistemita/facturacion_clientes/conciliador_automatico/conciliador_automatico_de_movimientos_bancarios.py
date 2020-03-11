
from ..models import MovimientoBancario, Cliente, FacturaCliente, PagoClienteTransferenciaALiqueed, DeudaCliente, FacturadorDeConsultor

class ConciliadorAutomaticoDeMovimientosBancarios:
    
    def conciliar_movimientos_no_conciliados(self):
        for movimiento_no_conciliado in MovimientoBancario.movimientos_no_conciliados():
            self.intentar_conciliar_movimiento(movimiento_no_conciliado)

    def intentar_conciliar_movimiento(self, movimiento_no_conciliado):
        lectorDeMovimiento = LectorDeMovimientoAbstracto.detectarTipoCorrectoDeMovimiento(movimiento_no_conciliado)()
        lectorDeMovimiento.conciliar(movimiento_no_conciliado)

class LectorDeMovimientoAbstracto:

    @staticmethod
    def detectarTipoCorrectoDeMovimiento(movimiento_no_conciliado):
        for clase_lector in LectorDeMovimientoAbstracto.__subclasses__():
            if clase_lector.es_lector_que_corresponde(movimiento_no_conciliado):
                return clase_lector

            
