"""Vistas del módulo de cliente."""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView

# Django REST Framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

# Models
from core.models.cliente import Cliente

# Forms
from core.forms import ClienteForm

# Serializers
from core.serializers import ClienteSerializer


class ClienteViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """Cliente View set."""

    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ClienteListView(PermissionRequiredMixin, ListView):
    """Vista para listar todos los clientes."""

    template_name = 'core/cliente_list.html'
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


class ClienteCreateView(PermissionRequiredMixin, CreateView):
    """Vista para crear un cliente."""

    model = Cliente
    form_class = ClienteForm
    permission_required = 'core.add_cliente'
    success_url = reverse_lazy('cliente-list')


class ClienteDetailView(PermissionRequiredMixin, DetailView):
    """Vista para ver el detalle de un cliente."""

    queryset = Cliente.objects.all()
    permission_required = 'core.view_cliente'


class ClienteUpdateView(PermissionRequiredMixin, UpdateView):
    """Vista para editar un cliente."""

    queryset = Cliente.objects.all()
    form_class = ClienteForm
    permission_required = 'core.change_cliente'
    success_url = reverse_lazy('cliente-list')


class ClienteDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar un cliente."""

    queryset = Cliente.objects.all()
    permission_required = 'core.delete_cliente'
    success_url = reverse_lazy('cliente-list')
