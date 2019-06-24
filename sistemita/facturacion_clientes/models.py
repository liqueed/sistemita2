from django.db import models
from decimal import *
from djmoney.models.fields import MoneyField, Money
from solo.models import SingletonModel
from django.db.models import Sum

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)

    def deuda(self):
        total_adeudado = DeudaCliente.objects.filter(cliente=self).aggregate(models.Sum('monto'))
        return Money(total_adeudado['monto__sum'], 'ARS')

class Consultor(models.Model):
    nombre = models.CharField(max_length=30)

    def saldo_pendiente_de_cobro_a_cliente(self):
        return MentoringPendienteDeCobro.saldo(self) + DeliveryIndividualPendienteDeCobro.saldo(self)

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
        super().save(*args, **kwargs)  # Call the "real" save() method.
        deuda_cliente = DeudaCliente(cliente=self.cliente, monto=self.monto, fecha=self.fecha)
        deuda_cliente.save()
        porc = PorcentajesAportadosAFondosYDelivery.get_solo()
        porc.aportar_a_fondos_por_nueva_factura(self)

    def definir_mentoring(self, mentor, porcentaje_para_mentoring_sobre_total_facturado):
        self.mentor = mentor
        self.porcentaje_para_mentoring_sobre_total_facturado = porcentaje_para_mentoring_sobre_total_facturado
        mentoring_pendiente_de_cobro = MentoringPendienteDeCobro(
            monto=self.ganancia*porcentaje_para_mentoring_sobre_total_facturado/100,
            factura=self,
            mentor=mentor)
        mentoring_pendiente_de_cobro.save()

    @property
    def ganancia(self):
        return self.monto - self.gastos

class PorcentajesAportadosAFondosYDelivery(SingletonModel):
    porcentaje_fondo_administrativo = 10
    porcentaje_fondo_liquido = 5
    porcentaje_delivery_y_mentoring = 85

    def aportar_a_fondos_por_nueva_factura(self, factura):
        fondo_administrativo_pendiente_de_cobro = FondoAdministrativoPendienteDeCobro(
            factura=factura, monto=factura.ganancia*self.porcentaje_fondo_administrativo/100)
        fondo_administrativo_pendiente_de_cobro.save()
        fondo_liquido_pendiente_de_cobro = FondoLiquidoPendienteDeCobro(
            factura=factura, monto=factura.ganancia*self.porcentaje_fondo_liquido/100)
        fondo_liquido_pendiente_de_cobro.save()
        delivery_pendiente_de_cobro = DeliveryPendienteDeCobro(
            factura=factura, monto=factura.ganancia*self.porcentaje_delivery_y_mentoring/100)
        delivery_pendiente_de_cobro.save()

# Cuentas
class DeudaCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField()
    
    
class FondoAdministrativoPendienteDeCobro(models.Model):
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField(auto_now=True)
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE)
    
    @classmethod
    def saldo(clase):
        return clase.objects.all().aggregate(Sum('monto'))['monto__sum']

class FondoLiquidoPendienteDeCobro(models.Model):
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField(auto_now=True)
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE)

    @classmethod
    def saldo(clase):
        return clase.objects.all().aggregate(Sum('monto'))['monto__sum']

class DeliveryPendienteDeCobro(models.Model):
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField(auto_now=True)
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE)
    
    def saldo():
        return DeliveryPendienteDeCobro.objects.all().aggregate(Sum('monto'))['monto__sum']

class MentoringPendienteDeCobro(models.Model):
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField(auto_now=True)
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE)
    mentor = models.ForeignKey(Consultor, on_delete=models.CASCADE)

    def saldo(mentor):
        return MentoringPendienteDeCobro.objects.filter(mentor=mentor).aggregate(Sum('monto'))['monto__sum']

class DeliveryIndividualPendienteDeCobro(models.Model):
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField(auto_now=True)
    factura = models.ForeignKey(FacturaCliente, on_delete=models.CASCADE)
    consultor = models.ForeignKey(Consultor, on_delete=models.CASCADE)

    def saldo(consultor):
        return DeliveryIndividualPendienteDeCobro.objects.filter(consultor=consultor).aggregate(Sum('monto'))['monto__sum']