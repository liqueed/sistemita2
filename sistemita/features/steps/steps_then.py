from facturacion_clientes import models
from django.db.models import Sum
from django.db import connection
from datetime import date
from djmoney.money import Money
from decimal import Decimal
from steps_common import *


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


@then(u'el saldo pendiente de cobro del fondo administrativo es de "{monto:d}" pesos')
def step_impl(context, monto):
    context.test.assertEquals(models.FondoAdministrativo.saldo_pendiente_de_cobro(), Decimal(monto))


@then(u'el saldo pendiente de cobro del fondo líquido es de "{monto:d}" pesos')
def step_impl(context, monto):
    context.test.assertEquals(models.FondoLiquido.saldo_pendiente_de_cobro(), Decimal(monto))


@then(u'el saldo pendiente de cobro de "{nombre_consultor}" con liqueed es de "{monto:d}"')
def step_impl(context, nombre_consultor, monto):
    consultor = models.Consultor.objects.get(nombre=nombre_consultor)
    context.test.assertEquals(consultor.saldo_pendiente_de_cobro_a_cliente(), Decimal(monto))


@then(u'el cliente "{nombre_cliente}" adeuda "{monto:d}" pesos')
def step_impl(context, nombre_cliente, monto):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    context.test.assertEquals(cliente.deuda(), Money(monto, 'ARS'))

@then(u'el "{a_fecha:tg}" faltarán "{dias_faltantes:d}" días para que "{nombre_cliente}" pague la última factura')
def step_impl(context, a_fecha, dias_faltantes, nombre_cliente):
    dias_faltantes_a_comparar = models.DeudaCliente.dias_faltantes_para_cobro(factura=context.ultima_factura, a_fecha=a_fecha.date())
    context.test.assertEquals(dias_faltantes, dias_faltantes_a_comparar)

@then(u'hay "{monto:d}" pesos pendientes de pago de "{nombre_cliente}" a liqueed')
def step_impl(context, monto, nombre_cliente):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    context.test.assertEquals(cliente.deuda_con_liqueed(), Money(monto, 'ARS'))

@then(u'hay "{monto:d}" pesos pendientes de pago de "{nombre_cliente}" directamente a "{nombre_consultor}"')
def step_impl(context, monto, nombre_cliente, nombre_consultor):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    consultor = models.Consultor.objects.get(nombre=nombre_consultor)
    context.test.assertEquals(cliente.deuda_con_consultor(consultor), Money(monto, 'ARS'))

@then(u'hay "{monto:d}" pesos pendientes de pago directamente a "{nombre_consultor}"')
def step_impl(context, monto, nombre_consultor):
    consultor = models.Consultor.objects.get(nombre=nombre_consultor)
    context.test.assertEquals(cliente.deuda_con_consultor(consultor), Money(monto, 'ARS'))

@then(u'el saldo disponible del fondo administrativo es de "{monto:d}" pesos')
def step_impl(context, monto):
    context.test.assertEquals(models.FondoAdministrativo.saldo_disponible(), Decimal(monto))

@then(u'el saldo disponible del fondo líquido es de "{monto:d}" pesos')
def step_impl(context, monto):
    context.test.assertEquals(models.FondoLiquido.saldo_disponible(), Decimal(monto))

@then(u'el saldo bruto disponible de cobro de "{nombre_consultor}" con liqueed es de "{monto:d}"')
def step_impl(context, nombre_consultor, monto):
    consultor = models.Consultor.objects.get(nombre=nombre_consultor)
    context.test.assertEquals(consultor.saldo_bruto_disponible_de_cobro(), Decimal(monto))

@then(u'la deuda total de clientes para el "{abreviatura_de_tipo_de_curso}" del "{fecha_curso:tg}" es de "{monto:d}" pesos')
def step_impl(context, abreviatura_de_tipo_de_curso, fecha_curso, monto):
    tipo_de_curso = models.TipoDeCursoPublico.objects.get(abreviatura=abreviatura_de_tipo_de_curso)
    curso = models.CursoPublico.objects.get(tipo_de_curso=tipo_de_curso, fecha=fecha_curso)
    context.test.assertEquals(curso.monto_adeudado, Money(monto, 'ARS'))

@then(u'el total pagado por impuesto al cheque hasta el momento es "{monto:d}"')
def step_impl(context, monto):
    total_hasta_el_momento = models.PagoImpuestoAlCheque.total_hasta_el_momento()
    context.test.assertEquals(total_hasta_el_momento, Money(monto, 'ARS'))

@then(u'el consultor "{nombre_consultor}" ya no tiene delivery pendiente de cobro')
def step_impl(context, nombre_consultor):
    consultor = models.Consultor.objects.get(nombre=nombre_consultor)
    context.test.assertEquals(models.DeliveryIndividual.saldo_disponible(consultor), Decimal(0.0))