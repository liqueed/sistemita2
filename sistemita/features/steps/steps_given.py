from facturacion_clientes import models

@given(u'que "{nombre_cliente}" es cliente')
def step_impl(context, nombre_cliente):
    cliente = models.Cliente(nombre=nombre_cliente)
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