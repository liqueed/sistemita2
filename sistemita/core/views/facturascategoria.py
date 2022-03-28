"""Vistas del modelo FacturaCategoria."""

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
from sistemita.core.forms.clientes import FacturaCategoriaForm
from sistemita.core.models.cliente import FacturaCategoria
from sistemita.core.views.home import error_403
from sistemita.utils.commons import get_deleted_objects
from sistemita.utils.strings import (
    _MESSAGE_SUCCESS_CREATED,
    _MESSAGE_SUCCESS_DELETE,
    _MESSAGE_SUCCESS_UPDATE,
    MESSAGE_403,
)


class FacturaCategoriaListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que retorna un listado con las categoría."""

    paginate_by = 10
    permission_required = 'core.list_facturacategoria'
    raise_exception = True

    def get_queryset(self):
        """
        Sobreescribe queryset.
        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = FacturaCategoria.objects.order_by('nombre')
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


class FacturaCategoriaCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que agrega una categoría de factura."""

    form_class = FacturaCategoriaForm
    model = FacturaCategoria
    permission_required = 'core.add_facturacategoria'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_CREATED.format('categoría de factura')

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_facturacategoria'):
            return reverse('core:facturacategoria-update', args=(self.object.id,))
        if self.request.user.has_perm('core.view_facturacategoria'):
            return reverse('core:facturacategoria-detail', args=(self.object.id,))
        if self.request.user.has_perm('core.list_facturacategoria'):
            return reverse('core:facturacategoria-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaCategoriaDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una categoría de factura."""

    model = FacturaCategoria
    permission_required = 'core.view_facturacategoria'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaCategoriaUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un categoría de factura."""

    form_class = FacturaCategoriaForm
    model = FacturaCategoria
    permission_required = 'core.change_facturacategoria'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_UPDATE.format('categoría de factura')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('core:facturacategoria-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaCategoriaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina un categoría de factura."""

    model = FacturaCategoria
    permission_required = 'core.delete_facturacategoria'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_DELETE.format('categoría de factura')
    success_url = reverse_lazy('core:facturacategoria-list')

    def get_context_data(self, **kwargs):
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        deletable_objects, model_count, protected = get_deleted_objects([self.object])
        context['deletable_objects'] = deletable_objects
        context['model_count'] = dict(model_count).items()
        context['protected'] = protected
        return context

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
