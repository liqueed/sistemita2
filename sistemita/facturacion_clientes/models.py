from django.db import models
from decimal import *
from djmoney.models.fields import MoneyField, Money
from solo.models import SingletonModel
from django.db.models import Sum
from datetime import timedelta

def ResultadoAggregateAMoney(resultado):
    if (resultado==None):
        return Decimal('0')
    else:
        return resultado


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    cuit = models.BigIntegerField(null=True)
    dias_demora_pago = models.IntegerField(default=0)
    descripcion_en_resumen_bancario = models.CharField(max_length=50)

    def deuda(self):
        total_adeudado = DeudaCliente.objects.filter(factura__cliente=self).aggregate(models.Sum('monto'))
        return Money(ResultadoAggregateAMoney(total_adeudado['monto__sum']), 'ARS')

    def deuda_con_liqueed(self):
        total_adeudado = DeudaCliente.objects.filter(factura__cliente=self, factura__facturadeliqueedacliente__isnull=False).aggregate(models.Sum('monto'))
        return Money(ResultadoAggregateAMoney(total_adeudado['monto__sum']), 'ARS')

    def deuda_con_consultor(self, consultor):
        total_adeudado = DeudaCliente.objects.filter(factura__cliente=self, factura__facturadeconsultoracliente__consultor=consultor).aggregate(models.Sum('monto'))
        return Money(ResultadoAggregateAMoney(total_adeudado['monto__sum']), 'ARS')

    @staticmethod
    def agregar_cliente_o_recuperar_si_ya_existe(nombre):
        clientes_con_el_mismo_nombre = Cliente.objects.filter(nombre=nombre)
        if(clientes_con_el_mismo_nombre.count()==0):
            nuevo_cliente = Cliente(nombre=nombre)
            nuevo_cliente.save()
            return nuevo_cliente
        else:
            return clientes_con_el_mismo_nombre[0]

class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()

class Consultor(models.Model):
    nombre = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Consultores"

    def __str__(self):
        return self.nombre

    def saldo_pendiente_de_cobro_a_cliente(self):
        return Mentoring.saldo_pendiente_de_cobro(self) + DeliveryIndividual.saldo_pendiente_de_cobro(self)

    def saldo_bruto_disponible_de_cobro(self):
        return Mentoring.saldo_disponible(self) + DeliveryIndividual.saldo_disponible(self)

class FacturadorDeConsultor(models.Model):
    consultor = models.ForeignKey(Consultor, on_delete=models.CASCADE)
    cuit = models.BigIntegerField(null=True)
    cbu = models.CharField(max_length=22, null=True)

    @staticmethod
    def es_cbu_de_algun_consultor(cbu_a_buscar):
        return FacturadorDeConsultor.objects.filter(cbu=cbu_a_buscar).count()>0


class FacturaClienteManager(models.Manager):
    def ganancia_hasta_hoy(self):
        facturas = self.all()
        ganancia = Decimal('0.00')
        for factura in facturas.iterator():
            ganancia = ganancia + factura.ganancia
        return ganancia
        

class FacturaCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField()
    descripcion = models.CharField(max_length=300)
    gastos = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    mentor = models.ForeignKey(Consultor, on_delete=models.CASCADE, null=True)
    porcentaje_para_mentoring_sobre_total_facturado = models.DecimalField(max_digits=2, decimal_places=2, default=0.0)

    objects = FacturaClienteManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) 
        deuda_cliente = DeudaCliente(factura=self, monto=self.monto, fecha=self.fecha)
        deuda_cliente.save()
        porc = PorcentajesAportadosAFondosYDelivery.get_solo()
        porc.aportar_a_fondos_por_nueva_factura(self)

    def definir_mentoring(self, mentor, porcentaje_para_mentoring_sobre_total_facturado):
        self.mentor = mentor
        self.porcentaje_para_mentoring_sobre_total_facturado = porcentaje_para_mentoring_sobre_total_facturado
        mentoring_pendiente_de_cobro = Mentoring(
            monto=self.ganancia*porcentaje_para_mentoring_sobre_total_facturado/100,
            factura=self,
            mentor=mentor)
        mentoring_pendiente_de_cobro.save()
    
    @property
    def delivery_pendiente_de_cobro(self):
        monto_pendiente_delivery_y_mentoring = DeliveryYMentoring.objects.get(factura=self).monto
        pendientes_mentoring = Mentoring.objects.filter(factura=self)
        if(pendientes_mentoring.count()>0):
            monto_pendiente_mentoring = pendientes_mentoring[0].monto
        else:
            monto_pendiente_mentoring = 0
        return monto_pendiente_delivery_y_mentoring - monto_pendiente_mentoring

    @property
    def ganancia(self):
        return self.monto - self.gastos

    @property
    def monto_adeudado(self):
        monto_adeudado = Money(0.0, 'ARS')
        for deuda in DeudaCliente.objects.filter(factura=self):
            monto_adeudado = monto_adeudado + deuda.monto
        return monto_adeudado

class FacturaDeConsultorACliente(FacturaCliente):
    consultor = models.ForeignKey(Consultor, on_delete=models.CASCADE)

class FacturaDeLiqueedACliente(FacturaCliente):
    pass

class PorcentajesAportadosAFondosYDelivery(SingletonModel):
    porcentaje_fondo_administrativo = 10
    porcentaje_fondo_liquido = 5
    porcentaje_delivery_y_mentoring = 85

    def aportar_a_fondos_por_nueva_factura(self, factura):
        fondo_administrativo_pendiente_de_cobro = FondoAdministrativo(
            factura=factura, monto=factura.ganancia*self.porcentaje_fondo_administrativo/100)
        fondo_administrativo_pendiente_de_cobro.save()
        fondo_liquido_pendiente_de_cobro = FondoLiquido(
            factura=factura, monto=factura.ganancia*self.porcentaje_fondo_liquido/100)
        fondo_liquido_pendiente_de_cobro.save()
        delivery_y_mentoring_pendientes_de_cobro = DeliveryYMentoring(
            factura=factura, monto=factura.ganancia*self.porcentaje_delivery_y_mentoring/100)
        delivery_y_mentoring_pendientes_de_cobro.save()

# Cuentas
class DeudaCliente(models.Model):
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE)
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField()

    @staticmethod
    def dias_faltantes_para_cobro(factura, a_fecha):
        delta =  timedelta(days=factura.cliente.dias_demora_pago) + DeudaCliente.objects.get(factura=factura).fecha - a_fecha
        return delta.days
    
class MovimientoCuenta(models.Model):
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField(auto_now=True)
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE)
    PENDIENTE = 'PENDIENTE'
    DISPONIBLE = 'DISPONIBLE'
    COBRADO = 'COBRADO'
    POSIBLES_ESTADOS = (
        (PENDIENTE, 'Pendiente'),
        (DISPONIBLE, 'Disponible'),
        (COBRADO, 'Cobrado')
    )
    estado = models.CharField(
        max_length=10,
        choices=POSIBLES_ESTADOS,
        default=PENDIENTE
    )

    
    @classmethod
    def saldo_pendiente_de_cobro(clase):
        return ResultadoAggregateAMoney(
            clase.objects.filter(estado=MovimientoCuenta.PENDIENTE).aggregate(Sum('monto'))['monto__sum'])

    @classmethod
    def saldo_disponible(clase):
        return ResultadoAggregateAMoney(
            clase.objects.filter(estado=MovimientoCuenta.DISPONIBLE).aggregate(Sum('monto'))['monto__sum'])
    

class FondoAdministrativo(MovimientoCuenta):
    pass

class FondoLiquido(MovimientoCuenta):
    pass

class DeliveryYMentoring(MovimientoCuenta):
    pass

class Mentoring(MovimientoCuenta):
    mentor = models.ForeignKey(Consultor, on_delete=models.CASCADE)

    @staticmethod
    def saldo_pendiente_de_cobro(mentor):
        saldo = Mentoring.objects.filter(mentor=mentor, estado=MovimientoCuenta.PENDIENTE).aggregate(Sum('monto'))['monto__sum']
        return ResultadoAggregateAMoney(saldo)

    @staticmethod
    def saldo_disponible(mentor):
        saldo = Mentoring.objects.filter(mentor=mentor, estado=MovimientoCuenta.DISPONIBLE).aggregate(Sum('monto'))['monto__sum']
        return ResultadoAggregateAMoney(saldo)

class DeliveryIndividual(MovimientoCuenta):
    consultor = models.ForeignKey(Consultor, on_delete=models.CASCADE)

    @staticmethod
    def saldo_pendiente_de_cobro(consultor):
        saldo = DeliveryIndividual.objects.filter(consultor=consultor, estado=MovimientoCuenta.PENDIENTE).aggregate(Sum('monto'))['monto__sum']
        return ResultadoAggregateAMoney(saldo)

    @staticmethod
    def saldo_disponible(consultor):
        saldo = DeliveryIndividual.objects.filter(consultor=consultor, estado=MovimientoCuenta.DISPONIBLE).aggregate(Sum('monto'))['monto__sum']
        return ResultadoAggregateAMoney(saldo)

class MovimientoBancario(models.Model):
    fecha = models.DateField()
    codigo_sucursal = models.CharField(max_length=4)
    descripcion_sucursal = models.CharField(max_length=20)
    codigo_operativo = models.CharField(max_length=4)
    referencia = models.CharField(max_length=9)
    concepto = models.CharField(max_length=200)
    importe_pesos = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    saldo_pesos = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')

    @staticmethod
    def movimientos_no_conciliados():
        return MovimientoBancario.objects.filter(pagoclientetransferenciaaliqueed__isnull = True,
        pagoliqueedaconsultor__isnull = True,
        pagotarjetadecreditocorporativa__isnull = True,
        pagoimpuestoalcheque__isnull = True)

class PagoCliente(models.Model):
    class Meta:
        abstract = True

    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField(auto_now=True)
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        deuda_cancelada = DeudaCliente.objects.get(factura=self.factura)
        deuda_cancelada.delete()
        MovimientoCuenta.objects.filter(factura=self.factura).update(estado=MovimientoCuenta.DISPONIBLE)

class PagoClienteTransferenciaALiqueed(PagoCliente):
    movimiento_bancario = models.ForeignKey(MovimientoBancario, on_delete=models.CASCADE)

class PagoClienteTransferenciaAConsultor(PagoCliente):
    pass

class PagoLiqueedAConsultor(models.Model):
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField(auto_now=True)
    consultor = models.ForeignKey(Consultor, on_delete=models.CASCADE)
    facturador = models.ForeignKey(FacturadorDeConsultor, on_delete=models.CASCADE)
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE, null=True)
    movimiento_bancario = models.ForeignKey(MovimientoBancario, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.DescontarOEliminarDeudaLiqueedConConsultor()

    def DescontarOEliminarDeudaLiqueedConConsultor(self):
        delivery_individual_original = DeliveryIndividual.objects.get(factura=self.factura)
        if(self.monto < delivery_individual_original.monto):
            delivery_individual_pendiente = DeliveryIndividual(consultor=delivery_individual_original.consultor,
            factura=delivery_individual_original.factura,
            monto=delivery_individual_original.monto - self.monto,
            estado=delivery_individual_original.estado)
            delivery_individual_pendiente.save()
        delivery_individual_original.delete()
        
    
class PagoImpuestoAlCheque(models.Model):
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField(auto_now=True)
    pago = models.ForeignKey(PagoClienteTransferenciaALiqueed, on_delete=models.CASCADE)
    movimiento_bancario = models.ForeignKey(MovimientoBancario, on_delete=models.CASCADE)

    @staticmethod
    def total_hasta_el_momento():
        total = PagoImpuestoAlCheque.objects.aggregate(models.Sum('monto'))
        return Money(ResultadoAggregateAMoney(total['monto__sum']), 'ARS')
        

class TipoDeCursoPublico(models.Model):
    titulo = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=10)

class CursoPublico(models.Model):
    fecha = models.DateField()
    dictante = models.ForeignKey(Consultor, on_delete=models.CASCADE)
    tipo_de_curso = models.ForeignKey(TipoDeCursoPublico, on_delete=models.CASCADE)

    @property
    def monto_adeudado(self):
        inscripciones = InscripcionEnCursoPublico.objects.filter(curso=self)
        deuda = Money(0.0, 'ARS')
        for inscripcion in inscripciones:
            deuda = deuda + inscripcion.factura.monto_adeudado
        return deuda

class InscripcionEnCursoPublico(models.Model):
    curso = models.ForeignKey(CursoPublico, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE, null=True)
    costo_por_persona = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    cantidad_inscriptos = models.IntegerField()
    inscriptos = models.ManyToManyField(Contacto)

    @property
    def costo_total(self):
        return self.costo_por_persona * self.cantidad_inscriptos

    def facturar(self, fecha):
        factura = FacturaDeLiqueedACliente(cliente=self.cliente,
                                           fecha=fecha,
                                           gastos=0.0,
                                           descripcion="Inscripción de {0} en {1}".format(self.cliente.nombre, self.curso.tipo_de_curso),
                                           monto=self.costo_total)
        factura.save()
        self.factura = factura
        self.save()

class TarjetaDeCreditoCorporativa(models.Model):
    tipo = models.CharField(max_length=30)

class PagoTarjetaDeCreditoCorporativa(models.Model):
    tarjeta = models.ForeignKey(TarjetaDeCreditoCorporativa, on_delete=models.CASCADE)
    movimiento_bancario = models.ForeignKey(MovimientoBancario, on_delete=models.CASCADE)

    @property
    def monto(self):
        return self.movimiento_bancario.monto

    @property
    def fecha(self):
        return self.movimiento_bancario.fecha