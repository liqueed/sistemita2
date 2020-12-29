"""Vistas del modelo Proveedor."""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse, reverse_lazy
# Django REST Framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

# Models
from core.models.proveedor import Proveedor

# Forms
from core.forms.proveedores import ProveedorForm

# Serializers
from core.serializers import ProveedorSerializer

# Views
from core.views.home import error_403

# Utils
from core.utils.strings import (
    MESSAGE_403, MESSAGE_SUCCESS_CREATED, MESSAGE_SUCCESS_UPDATE, MESSAGE_SUCCESS_DELETE
)


class ProveedorViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Proveedor view set."""

    queryset = Proveedor.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProveedorSerializer


class ProveedorListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que devuelve un listado de proveedores."""

    paginate_by = 10
    permission_required = 'core.list_proveedor'
    raise_exception = True

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = Proveedor.objects.order_by('id')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search) | Q(cuit__icontains=search)
            )
        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


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
        elif self.request.user.has_perm('core.view_proveedor'):
            return reverse('core:proveedor-detail', args=(self.object.id,))
        elif self.request.user.has_perm('core.list_proveedor'):
            return reverse('core:proveedor-list')
        else:
            return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class ProveedorDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de un proveedor."""

    model = Proveedor
    permission_required = 'core.view_proveedor'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


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
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class ProveedorDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina a un proveedor."""

    model = Proveedor
    permission_required = 'core.delete_proveedor'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('proveedor')
    success_url = reverse_lazy('core:proveedor-list')

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super(ProveedorDeleteView, self).delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)
