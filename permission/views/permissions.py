"""Vistas de permisos."""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

# Models
from django.contrib.auth.models import Permission

# Forms
from permission.forms import PermissionForm


class PermissionListView(PermissionRequiredMixin, ListView):
    """Vista de listado de permisos."""

    paginate_by = 10
    permission_required = 'auth.list_permission'
    template_name = 'permission/permission_list.html'

    def get_queryset(self):
        """Devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Permission.objects.filter(
             content_type__app_label__in=['accounting', 'auth', 'authorization', 'core'],
             content_type__model__in=[
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


class PermissionCreateView(PermissionRequiredMixin, CreateView):
    """Vista para crear un permiso."""

    form_class = PermissionForm
    permission_required = 'auth.add_permission'
    success_url = reverse_lazy('permission:permission-list')
    template_name = 'permission/permission_form.html'


class PermissionDetailView(PermissionRequiredMixin, DetailView):
    """Vista que devuelve el detalle de un permiso."""

    model = Permission
    permission_required = 'auth.view_permission'
    template_name = 'permission/permission_detail.html'


class PermisoUpdateView(PermissionRequiredMixin, UpdateView):
    """Vista para editar un permiso existente."""

    form_class = PermissionForm
    model = Permission
    permission_required = 'auth.change_permission'
    success_url = reverse_lazy('permission:permission-list')
    template_name = 'permission/permission_form.html'


class PermissionDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar n permiso."""

    model = Permission
    permission_required = 'auth.delete_permission'
    success_url = reverse_lazy('permission:permission-list')
    template_name = 'permission/permission_confirm_delete.html'
