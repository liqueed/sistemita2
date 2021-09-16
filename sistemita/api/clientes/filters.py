"""Filtros para el modelo cliente."""

# Django
from django.db.models import Q
from django_filters import rest_framework as filters

# Sistemita
from sistemita.core.models.cliente import Cliente, Factura


class ClienteFilterSet(filters.FilterSet):
    """Filtro de clientes."""

    razon_social__cuit__icontains = filters.CharFilter(method='search_by_razon_social_cuit')

    def search_by_razon_social_cuit(self, queryset, name, value):
        """Realiza un búsqueda por razón social y cuit."""
        if value:
            queryset = queryset.filter(Q(razon_social__icontains=value) | Q(cuit__icontains=value))
        return queryset

    class Meta:
        """Configuraciones del filter."""

        model = Cliente
        fields = ('razon_social', 'cuit')


class FacturaFilterSet(filters.FilterSet):
    """Filtro de factura de clientes."""

    numero__icontains = filters.CharFilter(method='search_by_numero')

    def search_by_numero(self, queryset, name, value):
        """Realiza un búsqueda número de factura."""
        if value:
            queryset = queryset.filter(numero__icontains=value)
        return queryset

    class Meta:
        """Configuraciones del filter."""

        model = Factura
        fields = ('cobrado', 'cliente', 'numero')
