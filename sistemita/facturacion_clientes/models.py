from django.db import models
from decimal import *

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        cuenta_cliente = CuentaCliente(cliente=self)
        cuenta_cliente.save()

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
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now=True)
    descripcion = models.CharField(max_length=300)
    gastos = models.DecimalField(max_digits=10, decimal_places=2)
    mentor = models.ForeignKey(Consultor, on_delete=models.CASCADE, null=True)

    objects = FacturaClienteManager()

    @property
    def ganancia(self):
        return self.monto - self.gastos

class CuentaCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)