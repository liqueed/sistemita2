from django_filters.rest_framework import BooleanFilter, FilterSet

from core.models import Factura


class FacturaFilterSet(FilterSet):
    cobrado = BooleanFilter()

    class Meta:
        model = Factura
        fields = ['cobrado']
