"""Vistas del modelo Cliente."""

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
from sistemita.core.forms.clientes import ClienteForm
from sistemita.core.models.cliente import Cliente
from sistemita.core.views.home import error_403
from sistemita.utils.commons import get_deleted_objects
from sistemita.utils.strings import (
    MESSAGE_403,
    MESSAGE_SUCCESS_CREATED,
    MESSAGE_SUCCESS_DELETE,
    MESSAGE_SUCCESS_UPDATE,
)


class ClienteListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista para listar todos los clientes."""

    paginate_by = 10
    permission_required = 'core.list_cliente'
    raise_exception = True
    template_name = 'core/cliente_list.html'

    def get_queryset(self):
        """
        Sobreescribe queryset.
        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = Cliente.objects.order_by('razon_social')
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


class ClienteCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista para crear un cliente."""

    form_class = ClienteForm
    model = Cliente
    permission_required = 'core.add_cliente'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_CREATED.format('cliente')

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_cliente'):
            return reverse('core:cliente-update', args=(self.object.id,))
        if self.request.user.has_perm('core.view_cliente'):
            return reverse('core:cliente-detail', args=(self.object.id,))
        if self.request.user.has_perm('core.list_cliente'):
            return reverse('core:cliente-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class ClienteDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista para ver el detalle de un cliente."""

    model = Cliente
    permission_required = 'core.view_cliente'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class ClienteUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista para editar un cliente."""

    model = Cliente
    form_class = ClienteForm
    permission_required = 'core.change_cliente'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_UPDATE.format('cliente')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('core:cliente-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class ClienteDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar un cliente."""

    model = Cliente
    permission_required = 'core.delete_cliente'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('cliente')
    success_url = reverse_lazy('core:cliente-list')

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
