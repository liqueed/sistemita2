"""Vistas de grupos."""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Forms
from authorization.forms.groups import GroupForm

# Models
from django.contrib.auth.models import Group

# Views
from core.views.home import error_403

# Utils
from core.utils.strings import (
    MESSAGE_403, MESSAGE_SUCCESS_CREATED, MESSAGE_SUCCESS_UPDATE, MESSAGE_SUCCESS_DELETE
)


class GroupListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Listado de Grupos."""

    paginate_by = 10
    permission_required = 'auth.list_group'
    raise_exception = True
    template_name = 'authorization/group_list.html'

    def get_queryset(self):
        """Devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Group.objects.order_by('id')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


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
        elif self.request.user.has_perm('auth.view_group'):
            return reverse('authorization:group-detail', args=(self.object.id,))
        elif self.request.user.has_perm('auth.list_group'):
            return reverse('authorization:group-list')
        else:
            return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class GroupDetailtView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista para ver el detalle de un grupo."""

    model = Group
    permission_required = 'auth.view_group'
    raise_exception = True
    template_name = 'authorization/group_detail.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


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
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


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
        return super(GroupDeleteView, self).delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)
