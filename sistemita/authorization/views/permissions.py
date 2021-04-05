"""Vistas de permisos."""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Forms
from authorization.forms.permissions import PermissionForm

# Models
from django.contrib.auth.models import Permission

# Views
from core.views.home import error_403

# Utils
from core.utils.strings import (
    MESSAGE_403, MESSAGE_SUCCESS_CREATED, MESSAGE_SUCCESS_UPDATE, MESSAGE_SUCCESS_DELETE
)


class PermissionListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista de que devuelve un listado de permisos."""

    paginate_by = 10
    permission_required = 'auth.list_permission'
    raise_exception = True
    template_name = 'authorization/permission_list.html'

    def get_queryset(self):
        """Devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Permission.objects.filter(
             content_type__app_label__in=['accounting', 'auth', 'authorization', 'core'],
             content_type__model__in=[
                 'archivo',
                 'cliente', 'factura', 'ordencompra', 'cobranza',
                 'proveedor', 'facturaproveedor', 'pago',
                 'mediopago',
                 'permission', 'user', 'group'
             ]
        ).order_by('content_type__model', 'name')
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class PermissionCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista para crear un permiso."""

    form_class = PermissionForm
    permission_required = 'auth.add_permission'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_CREATED.format('permiso')
    template_name = 'authorization/permission_form.html'

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('auth.change_permission'):
            return reverse('authorization:permission-update', args=(self.object.id,))
        elif self.request.user.has_perm('auth.view_permission'):
            return reverse('authorization:permission-detail', args=(self.object.id,))
        elif self.request.user.has_perm('auth.list_permission'):
            return reverse('authorization:permission-list')
        else:
            return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class PermissionDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que devuelve el detalle de un permiso."""

    model = Permission
    permission_required = 'auth.view_permission'
    raise_exception = True
    template_name = 'authorization/permission_detail.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class PermisoUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista para editar un permiso existente."""

    form_class = PermissionForm
    model = Permission
    permission_required = 'auth.change_permission'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_UPDATE.format('permiso')
    template_name = 'authorization/permission_form.html'

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('authorization:permission-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class PermissionDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar n permiso."""

    model = Permission
    permission_required = 'auth.delete_permission'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('permiso')
    success_url = reverse_lazy('authorization:permission-list')
    template_name = 'authorization/permission_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super(PermissionDeleteView, self).delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)
