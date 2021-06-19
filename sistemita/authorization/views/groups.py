"""Vistas de grupos."""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Authorization
from sistemita.authorization.forms.groups import GroupForm
from sistemita.core.utils.strings import (
    MESSAGE_403,
    MESSAGE_SUCCESS_CREATED,
    MESSAGE_SUCCESS_DELETE,
    MESSAGE_SUCCESS_UPDATE,
)

# Core
from sistemita.core.views.home import error_403


class GroupListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Listado de Grupos."""

    model = Group
    permission_required = 'auth.list_group'
    raise_exception = True
    template_name = 'authorization/group_list.html'
    ordering = ['name']

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['count'] = queryset.count()
        return context


class GroupCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista para crear un grupo."""

    form_class = GroupForm
    model = Group
    permission_required = 'auth.add_group'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_CREATED.format('grupo')
    success_url = reverse_lazy('authorization:group-list')
    template_name = 'authorization/group_form.html'

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('auth.change_group'):
            return reverse('authorization:group-update', args=(self.object.id,))
        if self.request.user.has_perm('auth.view_group'):
            return reverse('authorization:group-detail', args=(self.object.id,))
        if self.request.user.has_perm('auth.list_group'):
            return reverse('authorization:group-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class GroupDetailtView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista para ver el detalle de un grupo."""

    model = Group
    permission_required = 'auth.view_group'
    raise_exception = True
    template_name = 'authorization/group_detail.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class GroupUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista para editar un grupo."""

    form_class = GroupForm
    model = Group
    permission_required = 'auth.change_group'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_UPDATE.format('grupo')
    template_name = 'authorization/group_form.html'

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('authorization:group-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class GroupDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar un grupo."""

    model = Group
    permission_required = 'auth.delete_group'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('grupo')
    success_url = reverse_lazy('authorization:group-list')
    template_name = 'authorization/group_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
