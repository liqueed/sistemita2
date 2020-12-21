"""Vistas del módulo de facturación a proveedores."""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django_filters.views import FilterView

# Django REST Framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

# Models
from core.models.proveedor import FacturaProveedor

# Filters
from core.filters import FacturaProveedorFilterSet

# Forms
from core.forms import FacturaProveedorForm

# Serializers
from core.serializers import FacturaProveedorSerializer


class FacturaProveedorViewSet(mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    """Factura de proveedores view ser."""

    queryset = FacturaProveedor.objects.all()
    serializer_class = FacturaProveedorSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_fields = ('proveedor', 'cobrado')


class FacturaProveedorListView(PermissionRequiredMixin, FilterView):
    """Vista que retorna un lista de facturas a proveedores."""

    filterset_class = FacturaProveedorFilterSet
    permission_required = 'core.list_facturaproveedor'

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = FacturaProveedor.objects.all()

        search = self.request.GET.get('search', None)
        if search:
            self.queryset = queryset.filter(
                Q(proveedor__razon_social__icontains=search) |
                Q(proveedor__correo__icontains=search) |
                Q(proveedor__cuit__icontains=search)
            )

        return self.queryset


class FacturaProveedorCreateView(PermissionRequiredMixin, CreateView):
    """Vista que create un factura a proveedor."""

    model = FacturaProveedor
    form_class = FacturaProveedorForm
    permission_required = 'core.add_facturaproveedor'
    success_url = reverse_lazy('facturaproveedor-list')


class FacturaProveedorDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra el detalle de una factura a proveedor."""

    queryset = FacturaProveedor.objects.all()
    permission_required = 'core.view_facturaproveedor'


class FacturaProveedorUpdateView(PermissionRequiredMixin, UpdateView):
    """Vista que modifica la factura a proveedor."""

    queryset = FacturaProveedor.objects.all()
    form_class = FacturaProveedorForm
    permission_required = 'core.change_facturaproveedor'
    success_url = reverse_lazy('facturaproveedor-list')


class FacturaProveedorDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina una factura a proveedor."""

    queryset = FacturaProveedor.objects.all()
    permission_required = 'core.delete_facturaproveedor'
    success_url = reverse_lazy('facturaproveedor-list')

    def delete(self, request, *args, **kwargs):
        """Método que elimina los archivos relacionados."""
        self.object = self.get_object()
        self.object.archivos.all().delete()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
