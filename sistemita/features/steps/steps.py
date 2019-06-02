from facturacion_clientes import models
from django.db.models import Sum
from django.db import connection
from datetime import date
from djmoney.money import Money

@given(u'que "{nombre_cliente}" es cliente')
def step_impl(context, nombre_cliente):
    cliente = models.Cliente(nombre=nombre_cliente)
    cliente.save()    

def crear_factura(nombre_cliente, ingreso, gastos, fecha, context):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    factura = models.FacturaCliente(
        cliente=cliente, 
        monto=ingreso, 
        gastos=gastos,
        fecha=fecha
    )
    factura.save()
    context.ultima_factura = factura

@when(u'se facture hoy "{monto:d}" pesos a "{nombre_cliente}" sin gastos')
def step_impl(context, monto, nombre_cliente):
    crear_factura(nombre_cliente, monto, Money(0, 'ARS'), date.today(), context)

@when(u'se facture "{ingreso:d}" pesos el "{fecha:tg}" al cliente "{nombre_cliente}" con "{gastos:d}" pesos de gastos')
def step_impl(context, ingreso, fecha, nombre_cliente, gastos):
    crear_factura(nombre_cliente, Money(ingreso,'ARS'),  Money(gastos, 'ARS'), fecha, context)

@then(u'la última factura fue de "{monto:d}" pesos realizada el "{fecha:tg}" al cliente "{nombre_cliente}" con "{gastos:d}" pesos de gastos')
def step_impl(context, monto, fecha, nombre_cliente, gastos):
    factura = context.ultima_factura
    context.test.assertEquals(Money(monto, 'ARS'), factura.monto)
    context.test.assertEquals(fecha, factura.fecha)
    context.test.assertEquals(nombre_cliente, factura.cliente.nombre)
    context.test.assertEquals(Money(gastos,'ARS'), factura.gastos)

@then(u'la ganancia obtenida por el trabajo hecho a "{nombre_cliente}" será de "{ganancia:d}" pesos')
def step_impl(context, nombre_cliente, ganancia):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    factura = models.FacturaCliente.objects.get(cliente=cliente)
    context.test.assertEquals(factura.ganancia, Money(ganancia, 'ARS'))

@then(u'la ganancia total obtenida por liqueed al día de hoy es de "{monto:d}" pesos')
def step_impl(context, monto):
    ganancia = models.FacturaCliente.objects.ganancia_hasta_hoy()
    context.test.assertEquals(ganancia, Money(monto, 'ARS'))


@given(u'que la distribución por default es del "{porcentaje_fondo_administrativo:d}%" para fondo administrativo, "{porcentaje_fondo_liquido:d}%" para el fondo líquido, "{porcentaje_mentoring:d}%" para mentoring y "{porcentaje_delivery:d}%" para el delivery')
def step_impl(context, porcentaje_fondo_administrativo, porcentaje_fondo_liquido, porcentaje_mentoring, porcentaje_delivery):
    raise NotImplementedError(u'FALTA')

@when(u'el mentoring lo hizo "{nombre_mentor}"')
def step_impl(context, nombre_mentor):
    factura = context.ultima_factura
    consultores = models.Consultor.objects.count()
    mentor = models.Consultor.objects.get(nombre=nombre_mentor)
    context.test.assertEquals(nombre_mentor, mentor.nombre)

@when(u'el reparto fue')
def step_impl(context):
    raise NotImplementedError(u'FALTA')

@then(u'el saldo del fondo administrativo es de "{monto:d}" pesos')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then el saldo del fondo administrativo es de "100" pesos')


@then(u'el saldo del fondo líquido es de "{monto:d}" pesos')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then el saldo del fondo líquido es de "50" pesos')


@then(u'el saldo de "{nombre_consultor}" con liqueed es de "{monto:d}"')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then el saldo de "David" con liqueed es de "525"')


@then(u'el cliente "{nombre_cliente}" adeuda "{monto:d}" pesos')
def step_impl(context, nombre_cliente, monto):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    context.test.assertEquals(cliente.deuda(), Money(monto, 'ARS'))