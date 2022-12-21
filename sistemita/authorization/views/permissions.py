"""Vistas de permisos."""

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

# Forms
from sistemita.authorization.forms.permissions import PermissionForm
from sistemita.authorization.models import Permission
from sistemita.core.views.home import error_403
from sistemita.utils.commons import get_deleted_objects
from sistemita.utils.strings import (
    MESSAGE_403,
    MESSAGE_SUCCESS_CREATED,
    MESSAGE_SUCCESS_DELETE,
    MESSAGE_SUCCESS_UPDATE,
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
            Q(content_type__app_label__in=['accounting', 'auth', 'authorization', 'core', 'expense'])
            | Q(
                content_type__model__in=[
                    'archivo',
                    'cliente',
                    'factura',
                    'facturadistribuida',
                    'facturaimputada',
                    'facturacategoria',
                    'ordencompra',
                    'cobranza',
                    'proveedor',
                    'facturaproveedor',
                    'facturaproveedorcategoria',
                    'facturaproveedorimputada',
                    'pago',
                    'mediopago',
                    'permission',
                    'user',
                    'group',
                    'fondo',
                    'costo',
                ]
            )
        ).order_by('content_type__model', 'name')

        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', None)
        try:
            if search:
                queryset = queryset.filter(name__icontains=search)
            if order_by:
                queryset = queryset.order_by(order_by)
        except FieldError:
            pass
        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


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
        if self.request.user.has_perm('auth.view_permission'):
            return reverse('authorization:permission-detail', args=(self.object.id,))
        if self.request.user.has_perm('auth.list_permission'):
            return reverse('authorization:permission-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class PermissionDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que devuelve el detalle de un permiso."""

    model = Permission
    permission_required = 'auth.view_permission'
    raise_exception = True
    template_name = 'authorization/permission_detail.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


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
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class PermissionDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar n permiso."""

    model = Permission
    permission_required = 'auth.delete_permission'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('permiso')
    success_url = reverse_lazy('authorization:permission-list')
    template_name = 'authorization/permission_confirm_delete.html'

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
