"""Filters del módulo Factura."""

# Django Filter
from django_filters.rest_framework import BooleanFilter, FilterSet

# Models
from sistemita.core.models.cliente import Factura
from sistemita.core.models.proveedor import FacturaProveedor


class FacturaFilterSet(FilterSet):
    """Filters de Factura."""

    cobrado = BooleanFilter()

    class Meta:
        """Configuraciones del filter."""

        model = Factura
        fields = ['cobrado']


class FacturaProveedorFilterSet(FilterSet):
    """Filters de FacturaProveedor."""

    cobrado = BooleanFilter()

    class Meta:
        """Configuraciones del filter."""

        model = FacturaProveedor
        fields = ['cobrado']
