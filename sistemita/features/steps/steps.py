from facturacion_clientes import models
from django.db.models import Sum
from django.db import connection
from datetime import date
from djmoney.money import Money
from decimal import *

@given(u'que "{nombre_cliente}" es cliente')
def step_impl(context, nombre_cliente):
    cliente = models.Cliente(nombre=nombre_cliente)
    cliente.save()    

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

@when(u'se facture desde liqueed hoy "{monto:d}" pesos a "{nombre_cliente}" sin gastos')
def step_impl(context, monto, nombre_cliente):
    crear_factura_de_liqueed_a_cliente(nombre_cliente, monto, Money(0, 'ARS'), date.today(), context)

@when(u'se facture desde liqueed "{ingreso:d}" pesos el "{fecha:tg}" al cliente "{nombre_cliente}" con "{gastos:d}" pesos de gastos')
def step_impl(context, ingreso, fecha, nombre_cliente, gastos):
    crear_factura_de_liqueed_a_cliente(nombre_cliente, Money(ingreso,'ARS'),  Money(gastos, 'ARS'), fecha, context)

@when(u'"{nombre_consultor}" facture "{ingreso:d}" pesos el "{fecha:tg}" directamente al cliente "{nombre_cliente}" con "{gastos:d}" pesos de gastos')
def step_impl(context, nombre_consultor, ingreso, fecha, nombre_cliente, gastos):
    crear_factura_de_consultor_a_cliente(
            nombre_consultor=nombre_consultor,
            nombre_cliente=nombre_cliente,
            ingreso=Money(ingreso,'ARS'),
            gastos=Money(gastos, 'ARS'),
            fecha=fecha,
            context=context)


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

@when(u'el mentoring lo hizo "{nombre_mentor}" con un peso del "{porcentaje_para_mentoring_sobre_total_facturado:d}%" sobre el total facturado')
def step_impl(context, nombre_mentor, porcentaje_para_mentoring_sobre_total_facturado):
    factura = context.ultima_factura
    mentor = models.Consultor.objects.get(nombre=nombre_mentor)
    factura.definir_mentoring(mentor=mentor, porcentaje_para_mentoring_sobre_total_facturado=porcentaje_para_mentoring_sobre_total_facturado)


@when(u'el reparto fue')
def step_impl(context):
    for reparto in context.table:
        nombre_consultor = reparto['Consultor']
        consultor = models.Consultor.objects.get(nombre=nombre_consultor)
        porcentaje_aporte = reparto['%']
        delivery_individual_pendiente_de_cobro = models.DeliveryIndividual(
                consultor=consultor,
                factura=context.ultima_factura,
                monto = Decimal(porcentaje_aporte)/100*context.ultima_factura.delivery_pendiente_de_cobro)
        delivery_individual_pendiente_de_cobro.save()

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

@given(u'que el cliente "{nombre_cliente}" demora los pagos "{dias_demora_pago}" días')
def step_impl(context, nombre_cliente, dias_demora_pago):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    cliente.dias_demora_pago = dias_demora_pago
    cliente.save()


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

@when(u'el cliente "{nombre_cliente}" pague la ultima factura por transferencia bancaria el "{fecha:tg}"')
def step_impl(context, nombre_cliente, fecha):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    pago = models.PagoClienteTransferenciaALiqueed(
            monto=context.ultima_factura.monto,
            fecha=fecha,
            factura=context.ultima_factura
        )
    pago.save()

@then(u'el saldo disponible del fondo administrativo es de "{monto:d}" pesos')
def step_impl(context, monto):
    context.test.assertEquals(models.FondoAdministrativo.saldo_disponible(), Decimal(monto))

@then(u'el saldo disponible del fondo líquido es de "{monto:d}" pesos')
def step_impl(context, monto):
    context.test.assertEquals(models.FondoLiquido.saldo_disponible(), Decimal(monto))

@then(u'el saldo disponible de cobro de "{nombre_consultor}" con liqueed es de "{monto:d}"')
def step_impl(context, nombre_consultor, monto):
    consultor = models.Consultor.objects.get(nombre=nombre_consultor)
    context.test.assertEquals(consultor.saldo_disponible_de_cobro(), Decimal(monto))

@given(u'que está publicado un "{abreviatura_de_tipo_de_curso}" el "{fecha:tg}" dictado por "{dictante}"')
def step_impl(context, abreviatura_de_tipo_de_curso, fecha, dictante):
    consultor = models.Consultor.objects.get(nombre=dictante)
    tipo_de_curso = models.TipoDeCursoPublico.objects.get(abreviatura=abreviatura_de_tipo_de_curso)
    nuevo_curso = models.CursoPublico(tipo_de_curso=tipo_de_curso, fecha=fecha, dictante=consultor)
    nuevo_curso.save()

@when(u'se inscriba "{nombre_persona}" en el "{abreviatura_de_tipo_de_curso}" del "{fecha:tg}" con un costo de "{costo_por_persona:d}" pesos')
def step_impl(context, nombre_persona, abreviatura_de_tipo_de_curso, fecha, costo_por_persona):
    cliente = models.Cliente.agregar_cliente_o_recuperar_si_ya_existe(nombre_persona)
    tipo_de_curso = models.TipoDeCursoPublico.objects.get(abreviatura=abreviatura_de_tipo_de_curso)
    curso = models.CursoPublico.objects.get(tipo_de_curso=tipo_de_curso, fecha=fecha)
    inscripcion = models.InscripcionEnCursoPublico(fecha_inscripcion=fecha, curso=curso, cliente=cliente, costo_por_persona=costo_por_persona, cantidad_inscriptos=1)
    inscripcion.save()

@when(u'se haya facturado el "{fecha_facturacion:tg}" la inscripción de "{nombre_persona}" en el "{abreviatura_de_tipo_de_curso}" del "{fecha_curso:tg}"')
def step_impl(context, fecha_facturacion, nombre_persona, abreviatura_de_tipo_de_curso, fecha_curso):
    cliente = models.Cliente.agregar_cliente_o_recuperar_si_ya_existe(nombre_persona)
    tipo_de_curso = models.TipoDeCursoPublico.objects.get(abreviatura=abreviatura_de_tipo_de_curso)
    curso = models.CursoPublico.objects.get(tipo_de_curso=tipo_de_curso, fecha=fecha_curso)
    inscripcion = models.InscripcionEnCursoPublico.objects.get(curso=curso, cliente=cliente)
    factura_inscripcion = models.FacturaDeLiqueedACliente(cliente=cliente, 
        fecha=fecha_facturacion,
        monto=inscripcion.costo_por_persona,
        gastos=Decimal('0.00'))
    factura_inscripcion.save()

@when(u'se el cliente "{nombre_cliente}" inscriba "{cantidad_personas}" personas en el "{abreviatura_de_tipo_de_curso}" del "{fecha_curso:tg}" con un costo de "{costo_por_persona:d}" pesos cada una')
def step_impl(context, nombre_cliente, cantidad_personas, abreviatura_de_tipo_de_curso, fecha_curso, costo_por_persona):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    tipo_de_curso = models.TipoDeCursoPublico.objects.get(abreviatura=abreviatura_de_tipo_de_curso)
    curso = models.CursoPublico.objects.get(tipo_de_curso=tipo_de_curso, fecha=fecha_curso)
    inscripcion = models.InscripcionEnCursoPublico(fecha_inscripcion=fecha_curso, curso=curso, cliente=cliente, costo_por_persona=costo_por_persona, cantidad_inscriptos=cantidad_personas)
    inscripcion.save()

@when(u'se haya facturado la inscripción de los participantes de "{nombre_cliente}" en el "{abreviatura_de_tipo_de_curso}" del "{fecha_curso:tg}"')
def step_impl(context, nombre_cliente, abreviatura_de_tipo_de_curso, fecha_curso):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    tipo_de_curso = models.TipoDeCursoPublico.objects.get(abreviatura=abreviatura_de_tipo_de_curso)
    curso = models.CursoPublico.objects.get(tipo_de_curso=tipo_de_curso, fecha=fecha_curso)
    inscripciones = models.InscripcionEnCursoPublico.objects.filter(curso=curso)
    for inscripcion in inscripciones:
        inscripcion.facturar(fecha_curso)

@then(u'la deuda total de clientes para el "{abreviatura_de_tipo_de_curso}" del "{fecha_curso:tg}" es de "{monto:d}" pesos')
def step_impl(context, abreviatura_de_tipo_de_curso, fecha_curso, monto):
    tipo_de_curso = models.TipoDeCursoPublico.objects.get(abreviatura=abreviatura_de_tipo_de_curso)
    curso = models.CursoPublico.objects.get(tipo_de_curso=tipo_de_curso, fecha=fecha_curso)
    context.test.assertEquals(curso.monto_adeudado, Money(monto, 'ARS'))