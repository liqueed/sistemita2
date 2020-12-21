"""Vistas del módulo de órdenes de compra."""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView

# Models
from core.models.cliente import OrdenCompra

# Forms
from core.forms import OrdenCompraForm


class OrdenCompraListView(PermissionRequiredMixin, ListView):
    """Vista que retorna un listado de órdenes de compras."""

    template_name = 'ordendecompra-list'
    permission_required = 'core.list_ordencompra'

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = OrdenCompra.objects.all()
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) |
                Q(correo__icontains=search) |
                Q(cuit__icontains=search)
            )

        return queryset


class OrdenCompraCreateView(PermissionRequiredMixin, CreateView):
    """Vista que agrega una orden de compra."""

    model = OrdenCompra
    form_class = OrdenCompraForm
    permission_required = 'core.add_ordencompra'
    success_url = reverse_lazy('ordencompra-list')


class OrdenCompraDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra el detalle de una orden de compra."""

    queryset = OrdenCompra.objects.all()
    permission_required = 'core.view_ordencompra'


class OrdenCompraUpdateView(PermissionRequiredMixin, UpdateView):
    """Vista que actualiza una orden de compra."""

    queryset = OrdenCompra.objects.all()
    form_class = OrdenCompraForm
    permission_required = 'core.change_ordencompra'
    success_url = reverse_lazy('ordencompra-list')


class OrdenCompraDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina una orden de compra."""

    queryset = OrdenCompra.objects.all()
    permission_required = 'core.delete_ordencompra'
    success_url = reverse_lazy('ordencompra-list')
