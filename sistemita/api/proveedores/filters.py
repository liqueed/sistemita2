"""Filtros para el modelo proveedor."""

# Django
from django.db.models import Q
from django_filters import rest_framework as filters

# Sistemita
from sistemita.core.models.proveedor import FacturaProveedor, Proveedor


class ProveedorFilterSet(filters.FilterSet):
    """Filtro de proveedores."""

    razon_social__cuit__icontains = filters.CharFilter(method='search_by_razon_social_cuit')

    def search_by_razon_social_cuit(self, queryset, name, value):
        """Realiza un búsqueda por razón social y cuit."""
        if value:
            queryset = queryset.filter(Q(razon_social__icontains=value) | Q(cuit__icontains=value))
        return queryset

    class Meta:
        """Configuraciones del filter."""

        model = Proveedor
        fields = ('razon_social', 'cuit')


class FacturaProveedorFilterSet(filters.FilterSet):
    """Filtro de factura de proveedores."""

    numero__icontains = filters.CharFilter(method='search_by_numero')

    def search_by_numero(self, queryset, name, value):
        """Realiza un búsqueda número de factura."""
        if value:
            queryset = queryset.filter(numero__icontains=value)
        return queryset

    class Meta:
        """Configuraciones del filter."""

        model = FacturaProveedor
        fields = ('cobrado', 'proveedor', 'numero')
