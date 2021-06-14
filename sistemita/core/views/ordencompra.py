"""Vistas del modelo OrdenCompra."""

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView

# Sistemita
from sistemita.core.filters import OrdenCompraFilterSet
from sistemita.core.forms.clientes import OrdenCompraForm
from sistemita.core.models.cliente import OrdenCompra
from sistemita.core.utils.strings import (
    _MESSAGE_SUCCESS_CREATED,
    _MESSAGE_SUCCESS_DELETE,
    _MESSAGE_SUCCESS_UPDATE,
    MESSAGE_403,
)
from sistemita.core.views.home import error_403


class OrdenCompraListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que retorna un listado de órdenes de compras."""

    filterset_class = OrdenCompraFilterSet
    paginate_by = 10
    permission_required = 'core.list_ordencompra'
    raise_exception = True
    template_name = 'core/ordencompra_list.html'

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        current_week = date.today().isocalendar()[1]

        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = OrdenCompra.objects.order_by('-creado')
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search) | Q(cuit__icontains=search)
            )

        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


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
        if self.request.user.has_perm('core.view_ordencompra'):
            return reverse('core:ordencompra-detail', args=(self.object.id,))
        if self.request.user.has_perm('core.list_ordencompra'):
            return reverse('core:ordencompra-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class OrdenCompraDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una orden de compra."""

    model = OrdenCompra
    permission_required = 'core.view_ordencompra'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


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
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


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
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
