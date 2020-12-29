"""Vistas del modelo OrdenCompra."""

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
from core.forms.clientes import OrdenCompraForm

# Views
from core.views.home import error_403

# Utils
from core.utils.strings import (
    MESSAGE_403, _MESSAGE_SUCCESS_CREATED, _MESSAGE_SUCCESS_UPDATE, _MESSAGE_SUCCESS_DELETE
)


class OrdenCompraListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que retorna un listado de órdenes de compras."""

    paginate_by = 10
    permission_required = 'core.list_ordencompra'
    raise_exception = True

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = OrdenCompra.objects.order_by('id')
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search) | Q(cuit__icontains=search)
            )

        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class OrdenCompraCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que agrega una orden de compra."""

    form_class = OrdenCompraForm
    model = OrdenCompra
    permission_required = 'core.add_ordencompra'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_CREATED.format('orden de compra')
    success_url = reverse_lazy('core:ordencompra-list')

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_ordencompra'):
            return reverse('core:ordencompra-update', args=(self.object.id,))
        elif self.request.user.has_perm('core.view_ordencompra'):
            return reverse('core:ordencompra-detail', args=(self.object.id,))
        elif self.request.user.has_perm('core.list_ordencompra'):
            return reverse('core:ordencompra-list')
        else:
            return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class OrdenCompraDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una orden de compra."""

    model = OrdenCompra
    permission_required = 'core.view_ordencompra'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class OrdenCompraUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que actualiza una orden de compra."""

    form_class = OrdenCompraForm
    model = OrdenCompra
    permission_required = 'core.change_ordencompra'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_UPDATE.format('orden de compra')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('core:ordencompra-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class OrdenCompraDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina una orden de compra."""

    model = OrdenCompra
    permission_required = 'core.delete_ordencompra'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_DELETE.format('orden compra')
    success_url = reverse_lazy('core:ordencompra-list')

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super(OrdenCompraDeleteView, self).delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)
