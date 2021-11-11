"""Comando para popular el tipo de moneda en pagos y cobranzas."""

# Django
from django.core.management.base import BaseCommand

# Sistemita
from sistemita.accounting.models.cobranza import Cobranza
from sistemita.accounting.models.pago import Pago


class Command(BaseCommand):
    """Popula fondos a partir de facturas de cliente."""

    def handle(self, *args, **options):
        """Controlador."""
        # Cobranza
        for cobranza in Cobranza.objects.all():
            monedas = []
            for cobranza_factura in cobranza.cobranza_facturas.all():
                monedas.append(cobranza_factura.factura.moneda)
            if len(monedas) == 1:
                cobranza.moneda = monedas[0]
                cobranza.save()
            else:
                if len(set(monedas)) == 1:
                    cobranza.moneda = monedas[0]
                    cobranza.save()

        # Pago
        for pago in Pago.objects.all():
            monedas = []
            for pago_factura in pago.pago_facturas.all():
                monedas.append(pago_factura.factura.moneda)
            if len(monedas) == 1:
                pago.moneda = monedas[0]
                pago.save()
            else:
                if len(set(monedas)) == 1:
                    pago.moneda = monedas[0]
                    pago.save()

        self.stdout.write(self.style.SUCCESS('Done'))
