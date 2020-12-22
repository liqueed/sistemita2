"""Vistas de permisos."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

# Models
from django.contrib.auth.models import Permission

# Forms
from accounting.forms import PermissionForm


class PermissionListView(LoginRequiredMixin, ListView):
    """Vista de listado de permisos."""

    template_name = 'accounting/permission_list.html'
    paginate_by = 10

    # def dispatch(self, request, *args, **kwargs):
    #     """Sobrescribe dispatch."""
    #     if not request.user.has_perm('whatson.delete_event'):
    #         raise PermissionDenied(
    #             "You do not have permission to delete events"
    #         )
    #     return super(PermisoListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Permission.objects.filter(
             content_type__app_label__in=['accounting', 'auth', 'authentication', 'core'],
             content_type__model__in=[
                 'cliente', 'factura', 'ordencompra', 'cobranza',
                 'proveedor', 'facturaproveedor', 'pago',
                 'mediopago',
                 'permission', 'user', 'group'
             ]
        )
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset


class PermissionCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear un permiso."""

    model = Permission
    form_class = PermissionForm
    template_name = 'accounting/permission_form.html'
    success_url = reverse_lazy('accounting:permission-list')


class PermissionDetailView(LoginRequiredMixin, DetailView):
    """Vista que devuelve el detalle de un permiso."""

    model = Permission
    template_name = 'accounting/permission_detail.html'


class PermisoUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar un permiso existente."""

    model = Permission
    form_class = PermissionForm
    template_name = 'accounting/permission_form.html'
    success_url = reverse_lazy('accounting:permission-list')


class PermissionDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar n permiso."""

    model = Permission
    template_name = 'accounting/permission_confirm_delete.html'
    success_url = reverse_lazy('accounting:permission-list')
