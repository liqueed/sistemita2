"""Comando para crear facturas distribuidas."""

# Django
from django.core.management.base import BaseCommand

# Sistemita
from sistemita.core.models.cliente import Factura, FacturaDistribuida


class Command(BaseCommand):
    """Popula fondos a partir de facturas de cliente."""

    def handle(self, *args, **options):
        """Controlador."""
        for factura in Factura.objects.all():
            FacturaDistribuida.objects.get_or_create(factura=factura)

        self.stdout.write(self.style.SUCCESS('Done'))
