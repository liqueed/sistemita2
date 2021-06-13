"""Vistas del modelo MedioPago."""

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Sistemita
from sistemita.core.forms.mediospago import MedioPagoForm
from sistemita.core.models.mediopago import MedioPago
from sistemita.core.utils.strings import (
    MESSAGE_403,
    MESSAGE_SUCCESS_CREATED,
    MESSAGE_SUCCESS_DELETE,
    MESSAGE_SUCCESS_UPDATE,
)
from sistemita.core.views.home import error_403


class MedioPagoListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que retorna un listado con los medios de pagos."""

    paginate_by = 10
    permission_required = 'core.list_mediopago'
    raise_exception = True

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
        queryset = MedioPago.objects.order_by('id')
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class MedioPagoCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que agrega un medio de pago."""

    form_class = MedioPagoForm
    model = MedioPago
    permission_required = 'core.add_mediopago'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_CREATED.format('medio de pago')

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_mediopago'):
            return reverse('core:mediopago-update', args=(self.object.id,))
        if self.request.user.has_perm('core.view_mediopago'):
            return reverse('core:mediopago-detail', args=(self.object.id,))
        if self.request.user.has_perm('core.list_mediopago'):
            return reverse('core:mediopago-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class MedioPagoDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detall de un medio de pago."""

    model = MedioPago
    permission_required = 'core.view_mediopago'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class MedioPagoUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un medio de pago."""

    form_class = MedioPagoForm
    model = MedioPago
    permission_required = 'core.change_mediopago'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_UPDATE.format('medio de pago')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('core:mediopago-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class MedioPagoDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina un medio de pago."""

    model = MedioPago
    permission_required = 'core.delete_mediopago'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('medio de pago')
    success_url = reverse_lazy('core:mediopago-list')

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
