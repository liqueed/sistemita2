"""Vistas del modelo FacturaProveedo rCategoria."""

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Sistemita
from sistemita.core.forms.proveedores import FacturaProveedorCategoriaForm
from sistemita.core.models.proveedor import FacturaProveedorCategoria
from sistemita.core.views.home import error_403
from sistemita.utils.strings import (
    _MESSAGE_SUCCESS_CREATED,
    _MESSAGE_SUCCESS_DELETE,
    _MESSAGE_SUCCESS_UPDATE,
    MESSAGE_403,
)


class FacturaProveedorCategoriaListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que retorna un listado con las categoría."""

    paginate_by = 10
    permission_required = 'core.list_facturaproveedorcategoria'
    raise_exception = True

    def get_queryset(self):
        """
        Sobreescribe queryset.
        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = FacturaProveedorCategoria.objects.order_by('nombre')
        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', None)
        try:
            if search:
                queryset = queryset.filter(nombre__icontains=search)
            if order_by:
                queryset = queryset.order_by(order_by)
        except FieldError:
            pass
        return queryset

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        current_week = date.today().isocalendar()[1]

        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaProveedorCategoriaCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que agrega una categoría de factura."""

    form_class = FacturaProveedorCategoriaForm
    model = FacturaProveedorCategoria
    permission_required = 'core.add_facturaproveedorcategoria'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_CREATED.format('categoría de factura')

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_facturaproveedorcategoria'):
            return reverse('core:facturaproveedorcategoria-update', args=(self.object.id,))
        if self.request.user.has_perm('core.view_facturaproveedorcategoria'):
            return reverse('core:facturaproveedorcategoria-detail', args=(self.object.id,))
        if self.request.user.has_perm('core.list_facturaproveedorcategoria'):
            return reverse('core:facturaproveedorcategoria-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaProveedorCategoriaDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una categoría de factura."""

    model = FacturaProveedorCategoria
    permission_required = 'core.view_facturaproveedorcategoria'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaProveedorCategoriaUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un categoría de factura."""

    form_class = FacturaProveedorCategoriaForm
    model = FacturaProveedorCategoria
    permission_required = 'core.change_facturaproveedorcategoria'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_UPDATE.format('categoría de factura')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('core:facturaproveedorcategoria-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaProveedorCategoriaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina un categoría de factura."""

    model = FacturaProveedorCategoria
    permission_required = 'core.delete_facturaproveedorcategoria'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_DELETE.format('categoría de factura')
    success_url = reverse_lazy('core:facturaproveedorcategoria-list')

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
