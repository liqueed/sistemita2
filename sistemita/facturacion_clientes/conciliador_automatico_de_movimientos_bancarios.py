
from .models import MovimientoBancario, Cliente, FacturaCliente, PagoClienteTransferenciaALiqueed, DeudaCliente

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

    def conciliar(self, movimiento_no_conciliado):
        texto_a_procesar = self.limpiar_texto_de_concepto(movimiento_no_conciliado)
        cuit = self.extraer_cuit(texto_a_procesar)
        nombre_cliente = self.extraer_nombre_cliente(texto_a_procesar)
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

    
    def extraer_nombre_cliente(self, texto_a_procesar):
        return texto_a_procesar[:-LectorDeMovimientoDePagoDeCliente.LARGO_CUIT].strip()

    def extraer_cuit(self, texto_a_procesar):
        return texto_a_procesar[-LectorDeMovimientoDePagoDeCliente.LARGO_CUIT:]

    def limpiar_texto_de_concepto(self, movimiento_no_conciliado):
        texto_a_procesar = movimiento_no_conciliado.concepto
        texto_a_procesar = texto_a_procesar[LectorDeMovimientoDePagoDeCliente.LARGO_PREFIJO:][:-LectorDeMovimientoDePagoDeCliente.LARGO_SUFIJO]
        return texto_a_procesar
            



