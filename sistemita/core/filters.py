"""Filters del módulo Factura."""

# Django Filter
from django_filters.rest_framework import BooleanFilter, DateFilter, FilterSet

# Models
from sistemita.core.models.cliente import Factura, OrdenCompra
from sistemita.core.models.proveedor import FacturaProveedor


class FacturaFilterSet(FilterSet):
    """Filters de Factura."""

    cobrado = BooleanFilter()
    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = Factura
        fields = ['cobrado', 'desde', 'hasta']


class OrdenCompraFilterSet(FilterSet):
    """Filters de orden de compra."""

    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = OrdenCompra
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
