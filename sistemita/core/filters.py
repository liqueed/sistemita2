"""Filters del módulo Factura."""

# Django Filter
from django_filters.rest_framework import BooleanFilter, DateFilter, FilterSet

# Models
from sistemita.core.models.cliente import Contrato, Factura, FacturaImputada
from sistemita.core.models.proveedor import (
    FacturaProveedor,
    FacturaProveedorImputada,
)


class FacturaFilterSet(FilterSet):
    """Filters de Factura."""

    cobrado = BooleanFilter()
    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = Factura
        fields = ['cobrado', 'desde', 'hasta']


class ContratoFilterSet(FilterSet):
    """Filters de orden de compra."""

    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = Contrato
        fields = ['desde', 'hasta']


class FacturaImputadaFilterSet(FilterSet):
    """Filters de Factura Imputadas."""

    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = FacturaImputada
        fields = ['desde', 'hasta']


class FacturaProveedorFilterSet(FilterSet):
    """Filters de FacturaProveedor."""

    cobrado = BooleanFilter()
    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = FacturaProveedor
        fields = ['cobrado', 'desde', 'hasta']


class FacturaProveedorImputadaFilterSet(FilterSet):
    """Filters de Factura Imputadas de proveeodr."""

    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = FacturaProveedorImputada
        fields = ['desde', 'hasta']
