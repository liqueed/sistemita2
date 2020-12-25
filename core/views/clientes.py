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

# Utils
from core.utils.strings import (
    MESSAGE_SUCCESS_CREATED, MESSAGE_SUCCESS_UPDATE, MESSAGE_SUCCESS_DELETE
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

    template_name = 'core/cliente_list.html'
    paginate_by = 10
    permission_required = 'core.list_cliente'

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = Cliente.objects.all()

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) |
                Q(correo__icontains=search) |
                Q(cuit__icontains=search)
            )

        return queryset


class ClienteCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista para crear un cliente."""

    model = Cliente
    form_class = ClienteForm
    permission_required = 'core.add_cliente'
    success_message = MESSAGE_SUCCESS_CREATED.format('cliente')

    def get_success_url(self):
        """Luego de agregar al objecto muestra la misma vista."""
        return reverse('cliente-update', args=(self.object.id,))


class ClienteDetailView(PermissionRequiredMixin, DetailView):
    """Vista para ver el detalle de un cliente."""

    model = Cliente
    permission_required = 'core.view_cliente'


class ClienteUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista para editar un cliente."""

    model = Cliente
    form_class = ClienteForm
    permission_required = 'core.change_cliente'
    success_message = MESSAGE_SUCCESS_UPDATE.format('cliente')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('cliente-update', args=(self.object.id,))


class ClienteDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar un cliente."""

    model = Cliente
    permission_required = 'core.delete_cliente'
    success_message = MESSAGE_SUCCESS_DELETE.format('cliente')
    success_url = reverse_lazy('cliente-list')

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super(ClienteDeleteView, self).delete(request, *args, **kwargs)
