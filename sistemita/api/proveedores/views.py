"""Viewset proveedores"""

# Django REST Framework
from rest_framework import mixins, permissions, viewsets

# Sistemita
from sistemita.api.proveedores.serializers import (
    FacturaProveedorSerializer,
    ProveedorSerializer,
)
from sistemita.core.models.proveedor import FacturaProveedor, Proveedor


class ProveedorViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Proveedor view set."""

    queryset = Proveedor.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProveedorSerializer


class FacturaProveedorViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Factura de proveedores view set."""

    filter_fields = ('proveedor', 'cobrado')
    queryset = FacturaProveedor.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FacturaProveedorSerializer
