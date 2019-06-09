from django.db import models
from decimal import *
from djmoney.models.fields import MoneyField, Money

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)

    def deuda(self):
        total_adeudado = DeudaCliente.objects.filter(cliente=self).aggregate(models.Sum('monto'))
        return Money(total_adeudado['monto__sum'], 'ARS')

class Consultor(models.Model):
    nombre = models.CharField(max_length=30)

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

    objects = FacturaClienteManager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        deuda = DeudaCliente(cliente=self.cliente, monto=self.monto, fecha=self.fecha)
        deuda.save()

    @property
    def ganancia(self):
        return self.monto - self.gastos

# Cuentas
class DeudaCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    monto = MoneyField(max_digits=10, decimal_places=2, default_currency='ARS')
    fecha = models.DateField()
    
class FondoAdministrativo():
    def saldo(self):
        pass
    