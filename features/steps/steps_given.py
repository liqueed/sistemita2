from sistemita.core.models.cliente import Cliente, Factura
from sistemita.core.models.proveedor import Proveedor, FacturaProveedor
import logging

@given(u'que se facturó "{monto_facturado:d}" pesos + IVA al cliente "{razon_social_cliente}"')
def step_impl(context, monto_facturado, razon_social_cliente):
    cliente = Cliente.objects.get(razon_social=razon_social_cliente)

    factura = Factura(cliente=cliente, numero="1", fecha="2020-01-01", neto=monto_facturado, total=monto_facturado*1.21)
    factura.save()
    
    
    context.ultima_factura_generada = factura
    
    logger = logging.getLogger(__name__)
    logger.info(factura)

@given(u'que el consultor "{razon_social_proveedor}" le facturó a liqueed "{monto_facturado:d}" pesos + IVA correspondientes a la última factura hecha a un cliente')
def step_impl(context,  razon_social_proveedor, monto_facturado,):
    proveedor = Proveedor.objects.get(razon_social=razon_social_proveedor)

    factura = FacturaProveedor(proveedor=proveedor, factura=context.ultima_factura_generada, numero="1", fecha="2020-01-01", neto=monto_facturado, total=monto_facturado*1.21)
    factura.save()

    context.ultima_factura_de_consultor_a_liqueed = factura
    
    logger = logging.getLogger(__name__)
    logger.info(factura)