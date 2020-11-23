from django_filters.rest_framework import BooleanFilter, FilterSet

from core.models.cliente import Factura
from core.models.proveedor import FacturaProveedor


class FacturaFilterSet(FilterSet):
    cobrado = BooleanFilter()

    class Meta:
        model = Factura
        fields = ['cobrado']


class FacturaProveedorFilterSet(FilterSet):
    cobrado = BooleanFilter()

    class Meta:
        model = FacturaProveedor
        fields = ['cobrado']
