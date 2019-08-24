from facturacion_clientes import models
from django.db.models import Sum
from django.db import connection
from datetime import date
from djmoney.money import Money
from decimal import Decimal
from steps_common import *


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

@when(u'el único consultor sea "{nombre_consultor}"')
def step_impl(context, nombre_consultor):
        consultor = models.Consultor.objects.get(nombre=nombre_consultor)
        delivery_individual_pendiente_de_cobro = models.DeliveryIndividual(
                consultor=consultor,
                factura=context.ultima_factura,
                monto = context.ultima_factura.delivery_pendiente_de_cobro)
        delivery_individual_pendiente_de_cobro.save()

@when(u'el cliente "{nombre_cliente}" pague la ultima factura por transferencia bancaria el "{fecha:tg}"')
def step_impl(context, nombre_cliente, fecha):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    pago = models.PagoClienteTransferenciaALiqueed(
            monto=context.ultima_factura.monto,
            fecha=fecha,
            factura=context.ultima_factura
        )
    pago.save()
    context.ultimo_pago = pago

@when(u'se pague "{monto:d}" pesos de impuesto al cheque por crédito por el último pago de un cliente')
def step_impl(context, monto):
    pago_impuesto_al_cheque = models.PagoImpuestoAlCheque(
            monto=Money(monto, 'ARS'),
            fecha=context.ultimo_pago.fecha,
            pago=context.ultimo_pago
    )
    pago_impuesto_al_cheque.save()

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

@when(u'liqueed le pague "{monto:d}" pesos por transferencia a "{nombre_consultor}" el "{fecha:tg}" en concepto de delivery')
def step_impl(context, monto, nombre_consultor, fecha):
    consultor = models.Consultor.objects.get(nombre=nombre_consultor)
    pago = models.PagoLiqueedAConsultor(
            consultor=consultor,
            monto=Money(monto, 'ARS'),
            fecha=fecha,
            factura=context.ultima_factura
    )
    pago.save()