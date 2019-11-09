from facturacion_clientes import models

@given(u'que "{nombre_cliente}" es cliente')
def step_impl(context, nombre_cliente):
    cliente = models.Cliente(nombre=nombre_cliente)
    cliente.save()

@given(u'que "{nombre_cliente}" es cliente referenciado como "{descripcion_en_resumen_bancario}" en el resumen bancario con CUIT "{cuit:d}"')
def step_impl(context, nombre_cliente, descripcion_en_resumen_bancario, cuit):
    cliente = models.Cliente(nombre=nombre_cliente,\
         descripcion_en_resumen_bancario=descripcion_en_resumen_bancario,\
         cuit=cuit)
    cliente.save()

@given(u'que el cliente "{nombre_cliente}" demora los pagos "{dias_demora_pago}" días')
def step_impl(context, nombre_cliente, dias_demora_pago):
    cliente = models.Cliente.objects.get(nombre=nombre_cliente)
    cliente.dias_demora_pago = dias_demora_pago
    cliente.save()

@given(u'que está publicado un "{abreviatura_de_tipo_de_curso}" el "{fecha:tg}" dictado por "{dictante}"')
def step_impl(context, abreviatura_de_tipo_de_curso, fecha, dictante):
    consultor = models.Consultor.objects.get(nombre=dictante)
    tipo_de_curso = models.TipoDeCursoPublico.objects.get(abreviatura=abreviatura_de_tipo_de_curso)
    nuevo_curso = models.CursoPublico(tipo_de_curso=tipo_de_curso, fecha=fecha, dictante=consultor)
    nuevo_curso.save()

@given(u'que el consultor "{nombre_consultor}" tiene la siguiente estrategia tributaria')
def step_impl(context, nombre_consultor):
    consultor = models.Consultor.objects.get(nombre=nombre_consultor)
    for facturador in context.table:
        nuevo_facturador = models.FacturadorDeConsultor(consultor=consultor,
        cuit=facturador['CUIT'],
        cbu=facturador['CBU'])
        nuevo_facturador.save()
    consultor.save()

@given(u'que en liqueed hay tarjetas de crédito corporativas "{tipo_tarjeta}"')
def step_impl(context, tipo_tarjeta):
    tarjeta_de_credito_corporativa = models.TarjetaDeCreditoCorporativa(tipo=tipo_tarjeta)
    tarjeta_de_credito_corporativa.save()