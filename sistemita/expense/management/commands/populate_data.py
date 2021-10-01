"""Comando para popular datos de fondos."""

# Django
from django.core.management.base import BaseCommand

# Sistemita
from sistemita.core.models.cliente import Factura
from sistemita.expense.models import Fondo


class Command(BaseCommand):
    """Popula fondos a partir de facturas de cliente."""

    def handle(self, *args, **options):
        """Controlador."""
        for factura in Factura.objects.all():
            if not Fondo.objects.filter(factura=factura).exists():
                Fondo.objects.create(factura=factura, monena=factura.moneda, monto=factura.porcentaje_fondo_monto)
        self.stdout.write(self.style.SUCCESS('Initial data done.'))