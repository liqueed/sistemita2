"""Vistas del modelo Proveedor."""

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Sistemita
from sistemita.core.forms.proveedores import ProveedorForm
from sistemita.core.models.proveedor import Proveedor
from sistemita.core.views.home import error_403
from sistemita.utils.commons import get_deleted_objects
from sistemita.utils.strings import (
    MESSAGE_403,
    MESSAGE_SUCCESS_CREATED,
    MESSAGE_SUCCESS_DELETE,
    MESSAGE_SUCCESS_UPDATE,
)


class ProveedorListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que devuelve un listado de proveedores."""

    paginate_by = 10
    permission_required = 'core.list_proveedor'
    raise_exception = True

    def get_queryset(self):
        """
        Sobreescribe queryset.
        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = Proveedor.objects.order_by('razon_social')
        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', None)
        try:
            if search:
                queryset = queryset.filter(Q(razon_social__icontains=search) | Q(cuit__icontains=search))
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


class ProveedorCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que agrega un proveedor."""

    form_class = ProveedorForm
    model = Proveedor
    permission_required = 'core.add_proveedor'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_CREATED.format('proveedor')

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_proveedor'):
            return reverse('core:proveedor-update', args=(self.object.id,))
        if self.request.user.has_perm('core.view_proveedor'):
            return reverse('core:proveedor-detail', args=(self.object.id,))
        if self.request.user.has_perm('core.list_proveedor'):
            return reverse('core:proveedor-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class ProveedorDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de un proveedor."""

    model = Proveedor
    permission_required = 'core.view_proveedor'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class ProveedorUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un proveedor."""

    form_class = ProveedorForm
    model = Proveedor
    permission_required = 'core.change_proveedor'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_UPDATE.format('proveedor')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('core:proveedor-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class ProveedorDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina a un proveedor."""

    model = Proveedor
    permission_required = 'core.delete_proveedor'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('proveedor')
    success_url = reverse_lazy('core:proveedor-list')

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
