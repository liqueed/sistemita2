"""Funciones utilitarias."""
# Utilities
import logging
import math
from decimal import Decimal
from time import time

# Django
from django.contrib.admin.utils import NestedObjects
from django.utils.encoding import force_text
from django.utils.text import capfirst

# Sistemita
from sistemita.core.constants import ZERO_DECIMAL

logger = logging.getLogger(__name__)


def round_decimals_up(number, decimals):
    """
    Returns a value rounded up to a specific number of decimal places.
    """
    if not isinstance(number, Decimal):
        number = Decimal(number)

    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    if decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    if decimals == 0:
        return math.ceil(number)

    factor = 10**decimals
    return math.ceil(number * factor) / factor


def get_porcentaje(total, percentage):
    """
    Devuelve un monto que corresponde al porcentaje de un total.
    """
    if isinstance(percentage, Decimal):
        percentage = float(percentage)
    return round_decimals_up(float(total) * percentage / 100, 2)


def get_porcentaje_agregado(amount, percentage):
    """
    Recibe un monto, le suma porcentaje y devuelve un total.
    """
    if isinstance(amount, Decimal):
        amount = float(amount)
    return round_decimals_up(amount + percentage * amount / 100, 2)


def get_total_factura(monto_facturas, monto_nota_de_credito):
    """
    Calcula el total factura de un factura_imputada.
    El total factura se calcula sumando las facturas imputadas y luego restando el total sin imputar
    de la nota de crédito. En caso de que la nota de crédito sea mayor a la suma de facturas el total
    factura es igual a cero.
    """
    return max(Decimal(monto_facturas) - Decimal(monto_nota_de_credito), ZERO_DECIMAL)


def get_deleted_objects(objs):
    """Obtiene la cantidad de instancias relacionadas a eliminar."""

    collector = NestedObjects(using='default')
    collector.collect(objs)

    def format_callback(obj):
        opts = obj._meta
        no_edit_link = f'{capfirst(opts.verbose_name)}, {force_text(obj)}'
        return no_edit_link

    to_delete = collector.nested(format_callback)
    protected = [format_callback(obj) for obj in collector.protected]
    model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}

    return to_delete, model_count, protected


def get_groups_to_panel(facturas):
    """Ordena las facturas para el panel de control."""

    status = [1, 2, 3, 4]
    # groups = []

    for _ in facturas:
        sub_group = []
        for st in status:
            match = None
            for index, item in enumerate(facturas):
                if item.status == st:
                    match = (index, item)
                    break

            if match is not None:
                sub_group.append(match[1])
                del facturas[match[0]]
            else:
                sub_group.append(0)

            # Verifica si el el subgrupo se completó
            if len(sub_group) == 4:
                return facturas, sub_group

    return facturas, sub_group


def get_time_duration_log(time_start, message):
    """Obtiene el tiempo de duración"""
    time_end = time()
    time_duration = (time_end - time_start) * 1000
    logger.info(f'{message} time duration: {time_duration} ms')
