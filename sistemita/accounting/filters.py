"""Filters del módulo cuentas."""

# Django Filter
from django_filters.rest_framework import BooleanFilter, DateFilter, FilterSet

# Models
from sistemita.accounting.models.cobranza import Cobranza
from sistemita.accounting.models.pago import Pago


class PagoFilterSet(FilterSet):
    """Filters de Pago."""

    pagado = BooleanFilter()
    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = Pago
        fields = ['pagado', 'desde', 'hasta']


class CobranzaFilterSet(FilterSet):
    """Filters de Cobranza."""

    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = Cobranza
        fields = ['desde', 'hasta']
