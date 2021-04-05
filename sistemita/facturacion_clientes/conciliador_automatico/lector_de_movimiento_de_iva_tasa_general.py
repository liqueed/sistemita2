from .conciliador_automatico_de_movimientos_bancarios import LectorDeMovimientoAbstracto
from ..models import *

class LectorDeMovimientoDeIVATasaGeneral(LectorDeMovimientoAbstracto):
    CODIGO_OPERATIVO_IVA_TASA_GENERAL = '3254'

    @staticmethod
    def es_lector_que_corresponde(movimiento_no_conciliado):
        return movimiento_no_conciliado.codigo_operativo == LectorDeMovimientoDeIVATasaGeneral.CODIGO_OPERATIVO_IVA_TASA_GENERAL

    def conciliar(self, movimiento_no_conciliado):
        pago_iva_tasa_general = PagoIVATasaGeneral(
            fecha = movimiento_no_conciliado.fecha,
            monto = abs(movimiento_no_conciliado.importe_pesos),
            movimiento_bancario = movimiento_no_conciliado
        )
        pago_iva_tasa_general.save()
