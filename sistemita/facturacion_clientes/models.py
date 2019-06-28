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
    dias_demora_pago = models.IntegerField(default=0)

    def deuda(self):
        total_adeudado = DeudaCliente.objects.filter(factura__cliente=self).aggregate(models.Sum('monto'))
        return Money(ResultadoAggregateAMoney(total_adeudado['monto__sum']), 'ARS')

    def deuda_con_liqueed(self):
        total_adeudado = DeudaCliente.objects.filter(factura__cliente=self, factura__facturadeliqueedacliente__isnull=False).aggregate(models.Sum('monto'))
        return Money(ResultadoAggregateAMoney(total_adeudado['monto__sum']), 'ARS')

    def deuda_con_consultor(self, consultor):
        total_adeudado = DeudaCliente.objects.filter(factura__cliente=self, factura__facturadeconsultoracliente__consultor=consultor).aggregate(models.Sum('monto'))
        return Money(ResultadoAggregateAMoney(total_adeudado['monto__sum']), 'ARS')

class Consultor(models.Model):
    nombre = models.CharField(max_length=30)

    def saldo_pendiente_de_cobro_a_cliente(self):
        return Mentoring.saldo_pendiente_de_cobro(self) + DeliveryIndividual.saldo_pendiente_de_cobro(self)

    def saldo_disponible_de_cobro(self):
        return Mentoring.saldo_disponible(self) + DeliveryIndividual.saldo_disponible(self)

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

class PagoClienteTransferenciaALiqueed(models.Model):
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField(auto_now=True)
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        deuda_cancelada = DeudaCliente.objects.get(factura=self.factura)
        deuda_cancelada.delete()
        MovimientoCuenta.objects.filter(factura=self.factura).update(estado=MovimientoCuenta.DISPONIBLE)