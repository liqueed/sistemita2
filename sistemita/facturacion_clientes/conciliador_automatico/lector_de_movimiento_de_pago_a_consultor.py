from .conciliador_automatico_de_movimientos_bancarios import LectorDeMovimientoAbstracto
from ..models import PagoLiqueedAConsultorSinConciliar, FacturadorDeConsultor

class LectorDeMovimientoDePagoAConsultor(LectorDeMovimientoAbstracto):
    CODIGO_OPERATIVO_TRANSFERENCIA_A_OTRAS_CUENTAS = '0824'
    
    LARGO_CBU = 22

    @staticmethod
    def es_lector_que_corresponde(movimiento_no_conciliado):
        cbu = movimiento_no_conciliado.concepto.strip()[-LectorDeMovimientoDePagoAConsultor.LARGO_CBU:]
        es_cbu_de_algun_consultor = FacturadorDeConsultor.es_cbu_de_algun_consultor(cbu)
        return movimiento_no_conciliado.codigo_operativo == LectorDeMovimientoDePagoAConsultor.CODIGO_OPERATIVO_TRANSFERENCIA_A_OTRAS_CUENTAS \
            and es_cbu_de_algun_consultor

    def conciliar(self, movimiento_no_conciliado):
        cbu = movimiento_no_conciliado.concepto.strip()[-LectorDeMovimientoDePagoAConsultor.LARGO_CBU:]
        facturador = FacturadorDeConsultor.objects.get(cbu=cbu)
        pago_a_consultor_sin_conciliar = PagoLiqueedAConsultorSinConciliar(
            monto=abs(movimiento_no_conciliado.importe_pesos),
            fecha=movimiento_no_conciliado.fecha,
            consultor=facturador.consultor,
            facturador=facturador,
            movimiento_bancario=movimiento_no_conciliado
        )
        pago_a_consultor_sin_conciliar.save()