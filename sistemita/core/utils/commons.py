"""Funciones utilitarias."""

from decimal import Decimal

from sistemita.core.constants import ZERO_DECIMAL


def get_porcentaje_agregado(amount, percentage):
    """
    Recibe un monto, le suma porcentaje y devuelve un total.
    """
    return round(amount + percentage * amount / 100, 2)


def get_total_factura(monto_facturas, monto_nota_de_credito):
    """
    Calcula el total factura de un factura_imputada.
    El total factura se calcula sumando las facturas imputadas y luego restando el total sin imputar
    de la nota de crédito. En caso de que la nota de crédito sea mayor a la suma de facturas el total
    factura es igual a cero.
    """
    return max(Decimal(monto_facturas) - Decimal(monto_nota_de_credito), ZERO_DECIMAL)
