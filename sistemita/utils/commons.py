"""Funciones utilitarias."""

# Django
# Utilities
from decimal import Decimal

from django.contrib.admin.utils import NestedObjects
from django.utils.encoding import force_text
from django.utils.text import capfirst

# Sistemita
from sistemita.core.constants import ZERO_DECIMAL


def get_porcentaje(total, percentage):
    """
    Devuelve un monto que corresponde al porcentaje de un total.
    """
    if isinstance(percentage, Decimal):
        percentage = float(percentage)
    return round(float(total) * percentage / 100, 2)


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
