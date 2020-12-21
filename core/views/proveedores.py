"""Vistas del módulo de proveedores."""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

# Django REST Framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

# Models
from core.models.proveedor import Proveedor

# Forms
from core.forms import ProveedorForm

# Serializers
from core.serializers import ProveedorSerializer


class ProveedorViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """Proveedor view ser."""

    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ProveedorListView(PermissionRequiredMixin, ListView):
    """Vista que devuelve un listado de proveedores."""

    permission_required = 'core.list_proveedor'

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = Proveedor.objects.all()

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) |
                Q(correo__icontains=search) |
                Q(cuit__icontains=search)
            )
        return queryset


class ProveedorCreateView(PermissionRequiredMixin, CreateView):
    """Vista que agrega un proveedor."""

    model = Proveedor
    form_class = ProveedorForm
    permission_required = 'core.add_proveedor'
    success_url = reverse_lazy('proveedor-list')


class ProveedorDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra el detalle de un proveedor."""

    queryset = Proveedor.objects.all()
    permission_required = 'core.view_proveedor'


class ProveedorUpdateView(PermissionRequiredMixin, UpdateView):
    """Vista que modifica un proveedor."""

    queryset = Proveedor.objects.all()
    form_class = ProveedorForm
    permission_required = 'core.change_proveedor'
    success_url = reverse_lazy('proveedor-list')


class ProveedorDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina a un proveedor."""

    queryset = Proveedor.objects.all()
    permission_required = 'core.delete_proveedor'
    success_url = reverse_lazy('proveedor-list')
