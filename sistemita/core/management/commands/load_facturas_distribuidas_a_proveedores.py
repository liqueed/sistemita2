"""Comando para crear facturas distribuidas a proveedores."""

# Django
from django.core.management.base import BaseCommand

# Sistemita
from sistemita.core.models.cliente import FacturaDistribuida
from sistemita.core.models.proveedor import FacturaProveedor


class Command(BaseCommand):
    """Popula las facturas distribuidas a proveedores faltantes."""

    def handle(self, *args, **options):
        """Controlador."""
        for factura_distribuida in FacturaDistribuida.objects.all():
            for factura_distribuida_proveedor in factura_distribuida.factura_distribuida_proveedores.all():
                if not factura_distribuida_proveedor.factura_proveedor:
                    factura_proveedor = FacturaProveedor.objects.filter(
                        proveedor=factura_distribuida_proveedor.proveedor,
                        neto=factura_distribuida_proveedor.monto,
                        facturas_distribuidas__isnull=True,
                    ).first()
                    if factura_proveedor:
                        factura_distribuida_proveedor.factura_proveedor = factura_proveedor
                        factura_distribuida_proveedor.save()

        self.stdout.write(self.style.SUCCESS('Done'))
