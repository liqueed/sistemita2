"""Filters del módulo Factura."""

# Django Filter
from django.db import models
from django import forms
from django_filters.rest_framework import BooleanFilter, DateFilter, FilterSet
from django_filters import rest_framework as filters

# Models
from accounting.models.pago import Pago


class PagoFilterSet(FilterSet):
    """Filters de Pago."""

    pagado = BooleanFilter()
    desde = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('gte'))
    hasta = DateFilter(input_formats=['%d/%m/%Y'], field_name='fecha', lookup_expr=('lte'))

    class Meta:
        """Configuraciones del filter."""

        model = Pago
        fields = ['pagado', 'desde', 'hasta']
