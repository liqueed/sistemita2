"""Filters del módulo expense."""

# Django Filter
from django_filters.rest_framework import DateFilter, FilterSet

# Models
from sistemita.expense.models import Costo, Fondo


class FondoFilterSet(FilterSet):
    """Filters de Fondo."""

    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='factura__fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='factura__fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = Fondo
        fields = ('factura',)


class CostoFilterSet(FilterSet):
    """Filters de Costo."""

    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = Costo
        fields = ('fecha',)
