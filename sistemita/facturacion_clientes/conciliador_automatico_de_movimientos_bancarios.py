
from .models import MovimientoBancario, Cliente, FacturaCliente, PagoClienteTransferenciaALiqueed, DeudaCliente

class ConciliadorAutomaticoDeMovimientosBancarios:
    
    @staticmethod
    def conciliar_movimientos_no_conciliados():
        for movimiento_no_conciliado in MovimientoBancario.movimientos_no_conciliados():
            ConciliadorAutomaticoDeMovimientosBancarios.intentar_conciliar_movimiento(movimiento_no_conciliado)

    @staticmethod
    def intentar_conciliar_movimiento(movimiento_no_conciliado):
        lectorDeMovimiento = LectorDeMovimientoAbstracto.detectarTipoCorrectoDeMovimiento(movimiento_no_conciliado)
        lectorDeMovimiento.conciliar(movimiento_no_conciliado)

class LectorDeMovimientoAbstracto:

    @staticmethod
    def detectarTipoCorrectoDeMovimiento(movimiento_no_conciliado):
        for clase_lector in LectorDeMovimientoAbstracto.__subclasses__():
            if clase_lector.es_lector_que_corresponde(movimiento_no_conciliado):
                return clase_lector

class LectorDeMovimientoDePagoDeCliente(LectorDeMovimientoAbstracto):
    CODIGO_OPERATIVO_PAGO_INTERBANKING_INT = '2376'
    CODIGO_OPERATIVO_PAGO_INTERBANKING_EXT = '2377'
    
    LARGO_PREFIJO = 38
    LARGO_SUFIJO = 11
    LARGO_CUIT = 11


    @staticmethod
    def es_lector_que_corresponde(movimiento_no_conciliado):
        return movimiento_no_conciliado.codigo_operativo == LectorDeMovimientoDePagoDeCliente.CODIGO_OPERATIVO_PAGO_INTERBANKING_EXT \
            or movimiento_no_conciliado.codigo_operativo == LectorDeMovimientoDePagoDeCliente.CODIGO_OPERATIVO_PAGO_INTERBANKING_INT

    @staticmethod
    def conciliar(movimiento_no_conciliado):
        texto_a_procesar = LectorDeMovimientoDePagoDeCliente.limpiar_texto_de_concepto(movimiento_no_conciliado)
        cuit = LectorDeMovimientoDePagoDeCliente.extraer_cuit(texto_a_procesar)
        nombre_cliente = LectorDeMovimientoDePagoDeCliente.extraer_nombre_cliente(texto_a_procesar)
        cliente = Cliente.objects.get(cuit=cuit, descripcion_en_resumen_bancario=nombre_cliente)
        monto = movimiento_no_conciliado.importe_pesos
        deudas = DeudaCliente.objects.filter(factura__cliente=cliente, monto=monto)
        factura = deudas[0].factura
        pago = PagoClienteTransferenciaALiqueed(
                monto=monto,
                fecha=movimiento_no_conciliado.fecha,
                factura=factura,
                movimiento_bancario=movimiento_no_conciliado
        )
        pago.save()

    
    @staticmethod
    def extraer_nombre_cliente(texto_a_procesar):
        return texto_a_procesar[:-LectorDeMovimientoDePagoDeCliente.LARGO_CUIT].strip()

    @staticmethod
    def extraer_cuit(texto_a_procesar):
        return texto_a_procesar[-LectorDeMovimientoDePagoDeCliente.LARGO_CUIT:]

    @staticmethod
    def limpiar_texto_de_concepto(movimiento_no_conciliado):
        texto_a_procesar = movimiento_no_conciliado.concepto
        texto_a_procesar = texto_a_procesar[LectorDeMovimientoDePagoDeCliente.LARGO_PREFIJO:][:-LectorDeMovimientoDePagoDeCliente.LARGO_SUFIJO]
        return texto_a_procesar
            



