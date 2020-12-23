"""Vistas del módulo de órdenes de compra."""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView

# Models
from core.models.cliente import OrdenCompra

# Forms
from core.forms import OrdenCompraForm

# Utils
from core.utils.strings import (
    _MESSAGE_SUCCESS_CREATED, _MESSAGE_SUCCESS_UPDATE, _MESSAGE_SUCCESS_DELETE
)


class OrdenCompraListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que retorna un listado de órdenes de compras."""

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


class OrdenCompraCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que agrega una orden de compra."""

    model = OrdenCompra
    form_class = OrdenCompraForm
    permission_required = 'core.add_ordencompra'
    success_message = _MESSAGE_SUCCESS_CREATED.format('orden de compra')
    success_url = reverse_lazy('ordencompra-list')

    def get_success_url(self):
        """Luego de agregar al objecto muestra la misma vista."""
        return reverse('ordencompra-update', args=(self.object.id,))


class OrdenCompraDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra el detalle de una orden de compra."""

    model = OrdenCompra
    permission_required = 'core.view_ordencompra'


class OrdenCompraUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que actualiza una orden de compra."""

    model = OrdenCompra
    form_class = OrdenCompraForm
    success_message = _MESSAGE_SUCCESS_UPDATE.format('orden de compra')
    permission_required = 'core.change_ordencompra'

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('ordencompra-update', args=(self.object.id,))


class OrdenCompraDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina una orden de compra."""

    model = OrdenCompra
    permission_required = 'core.delete_ordencompra'
    success_message = _MESSAGE_SUCCESS_DELETE.format('orden compra')
    success_url = reverse_lazy('ordencompra-list')

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super(OrdenCompraDeleteView, self).delete(request, *args, **kwargs)
