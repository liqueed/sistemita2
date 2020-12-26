"""Vistas del modelo FacturaProveedor."""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django_filters.views import FilterView
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse, reverse_lazy

# Django REST Framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

# Models
from core.models.proveedor import FacturaProveedor

# Filters
from core.filters import FacturaProveedorFilterSet

# Forms
from core.forms.proveedores import FacturaProveedorForm

# Serializers
from core.serializers import FacturaProveedorSerializer

# Utils
from core.utils.strings import (
    _MESSAGE_SUCCESS_CREATED, _MESSAGE_SUCCESS_UPDATE, _MESSAGE_SUCCESS_DELETE
)


class FacturaProveedorViewSet(mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    """Factura de proveedores view ser."""

    queryset = FacturaProveedor.objects.all()
    serializer_class = FacturaProveedorSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_fields = ('proveedor', 'cobrado')


class FacturaProveedorListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que retorna un lista de facturas a proveedores."""

    filterset_class = FacturaProveedorFilterSet
    paginate_by = 10
    permission_required = 'core.list_facturaproveedor'
    template_name = 'core/facturaproveedor_list.html'

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = FacturaProveedor.objects.order_by('id')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(proveedor__razon_social__icontains=search) |
                Q(proveedor__correo__icontains=search) |
                Q(proveedor__cuit__icontains=search)
            )

        return queryset


class FacturaProveedorCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que create un factura a proveedor."""

    model = FacturaProveedor
    form_class = FacturaProveedorForm
    permission_required = 'core.add_facturaproveedor'
    success_message = _MESSAGE_SUCCESS_CREATED.format('factura a proveedor')

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_facturaproveedor'):
            return reverse('facturaproveedor-update', args=(self.object.id,))
        elif self.request.user.has_perm('core.view_facturaproveedor'):
            return reverse('facturaproveedor-detail', args=(self.object.id,))
        elif self.request.user.has_perm('core.list_facturaproveedor'):
            return reverse('facturaproveedor-list')
        else:
            return reverse('home')


class FacturaProveedorDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una factura a proveedor."""

    model = FacturaProveedor
    permission_required = 'core.view_facturaproveedor'


class FacturaProveedorUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica la factura a proveedor."""

    model = FacturaProveedor
    form_class = FacturaProveedorForm
    permission_required = 'core.change_facturaproveedor'
    success_message = _MESSAGE_SUCCESS_UPDATE.format('factura a proveedor')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('facturaproveedor-update', args=(self.object.id,))


class FacturaProveedorDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina una factura a proveedor."""

    model = FacturaProveedor
    permission_required = 'core.delete_facturaproveedor'
    success_message = _MESSAGE_SUCCESS_DELETE.format('factura a proveedor')
    success_url = reverse_lazy('facturaproveedor-list')

    def delete(self, request, *args, **kwargs):
        """Método que elimina los archivos relacionados."""
        self.object = self.get_object()
        self.object.archivos.all().delete()
        self.object.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(self.success_url)
