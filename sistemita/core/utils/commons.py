"""Funciones utilitarias."""


def get_porcentaje_agregado(amount, percentage):
    """
    Recibe un monto, le suma porcentaje y devuelve un total.
    """
    return round(amount + percentage * amount / 100, 2)
