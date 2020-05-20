from facturacion_clientes import models

def crear_factura_de_liqueed_a_cliente(nombre_cliente, ingreso, gastos, fecha, context):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    factura = models.FacturaDeLiqueedACliente(
        cliente=cliente, 
        monto=ingreso, 
        gastos=gastos,
        fecha=fecha
    )
    factura.save()
    context.ultima_factura = factura

def crear_factura_de_consultor_a_cliente(nombre_consultor, nombre_cliente, ingreso, gastos, fecha, context):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    consultor = models.Consultor.objects.get(nombre=nombre_consultor)
    factura = models.FacturaDeConsultorACliente(
        consultor=consultor,
        cliente=cliente, 
        monto=ingreso, 
        gastos=gastos,
        fecha=fecha
    )
    factura.save()
    context.ultima_factura = factura

