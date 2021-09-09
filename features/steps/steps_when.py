from sistemita.core.models.proveedor import Proveedor
from sistemita.core.models.mediopago import MedioPago
from sistemita.accounting.models.pago import Pago, PagoFactura, PagoFacturaPago
import logging

@when(u'se le quiera pagar "{monto_a_pagar:d}" pesos al consultor "{razon_social_proveedor}" correspondientes a la última factura hecha a liqueed')
def step_impl(context, monto_a_pagar, razon_social_proveedor):
    proveedor = Proveedor.objects.get(razon_social=razon_social_proveedor)

    pago = Pago(proveedor=proveedor, fecha="2020-01-01",  total=monto_a_pagar*1.21)
    pago_asociado_a_factura = PagoFactura(pago=pago, factura=context.ultima_factura_de_consultor_a_liqueed)
    pagoPorTransferencia = MedioPago.objects.get(pk=1)
    pago_asociado_a_pago_por_factura = PagoFacturaPago(metodo=pagoPorTransferencia, pago_factura=pago_asociado_a_factura, monto=monto_a_pagar*1.21)
    pago.save()
    pago_asociado_a_factura.save()
    pago_asociado_a_pago_por_factura.save()
    
 