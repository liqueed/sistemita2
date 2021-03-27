from .conciliador_automatico_de_movimientos_bancarios import LectorDeMovimientoAbstracto
from ..models import *

class LectorDeMovimientoDeImpuestoAlCheque(LectorDeMovimientoAbstracto):
    CODIGO_OPERATIVO_IMPUESTO_AL_DEBITO = '4633'
    CODIGO_OPERATIVO_IMPUESTO_AL_CREDITO = '4637'

    @staticmethod
    def es_lector_que_corresponde(movimiento_no_conciliado):
        return movimiento_no_conciliado.codigo_operativo == LectorDeMovimientoDeImpuestoAlCheque.CODIGO_OPERATIVO_IMPUESTO_AL_DEBITO \
            or movimiento_no_conciliado.codigo_operativo == LectorDeMovimientoDeImpuestoAlCheque.CODIGO_OPERATIVO_IMPUESTO_AL_CREDITO

    def conciliar(self, movimiento_no_conciliado):
        pago_impuesto_al_cheque = PagoImpuestoAlCheque(
            fecha = movimiento_no_conciliado.fecha,
            monto = abs(movimiento_no_conciliado.importe_pesos),
            movimiento_bancario = movimiento_no_conciliado
        )
        pago_impuesto_al_cheque.save()