"""Vistas del modelo Cliente."""

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
from core.models.cliente import Cliente

# Forms
from core.forms.clientes import ClienteForm

# Serializers
from core.serializers import ClienteSerializer

# Views
from core.views.home import error_403

# Utils
from core.utils.strings import (
    MESSAGE_403, MESSAGE_SUCCESS_CREATED, MESSAGE_SUCCESS_UPDATE, MESSAGE_SUCCESS_DELETE
)


class ClienteViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """Cliente View set."""

    queryset = Cliente.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ClienteSerializer


class ClienteListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista para listar todos los clientes."""

    paginate_by = 10
    permission_required = 'core.list_cliente'
    raise_exception = True
    template_name = 'core/cliente_list.html'

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = Cliente.objects.order_by('id')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) |
                Q(correo__icontains=search) |
                Q(cuit__icontains=search)
            )

        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


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
        elif self.request.user.has_perm('core.view_cliente'):
            return reverse('core:cliente-detail', args=(self.object.id,))
        elif self.request.user.has_perm('core.list_cliente'):
            return reverse('core:cliente-list')
        else:
            return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class ClienteDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista para ver el detalle de un cliente."""

    model = Cliente
    permission_required = 'core.view_cliente'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


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
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class ClienteDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar un cliente."""

    model = Cliente
    permission_required = 'core.delete_cliente'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('cliente')
    success_url = reverse_lazy('core:cliente-list')

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super(ClienteDeleteView, self).delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)
