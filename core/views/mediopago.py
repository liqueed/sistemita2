"""Vistas del módulo de medios de pago."""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

# Django REST Framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

# Forms
from core.forms import MedioPagoForm

# Models
from core.models.mediopago import MedioPago

# Serializers
from core.serializers import MedioPagoSerializer


class MedioPagoViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """Medio de pago view set."""

    queryset = MedioPago.objects.all()
    serializer_class = MedioPagoSerializer
    permission_classes = (permissions.IsAuthenticated,)


class MedioPagoListView(PermissionRequiredMixin, ListView):
    """Vista que retorna un listado con los medios de pagos."""

    permission_required = 'core.list_mediopago'

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = MedioPago.objects.all()
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                nombre__icontains=search
            )
        return queryset


class MedioPagoCreateView(PermissionRequiredMixin, CreateView):
    """Vista que agrega un medio de pago."""

    model = MedioPago
    form_class = MedioPagoForm
    permission_required = 'core.add_mediopago'
    success_url = reverse_lazy('mediopago-list')


class MedioPagoDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra el detall de un medio de pago."""

    queryset = MedioPago.objects.all()
    permission_required = 'core.view_mediopago'


class MedioPagoUpdateView(PermissionRequiredMixin, UpdateView):
    """Vista que modifica un medio de pago."""

    queryset = MedioPago.objects.all()
    form_class = MedioPagoForm
    permission_required = 'core.change_mediopago'
    success_url = reverse_lazy('mediopago-list')


class MedioPagoDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina un medio de pago."""

    queryset = MedioPago.objects.all()
    permission_required = 'core.delete_mediopago'
    success_url = reverse_lazy('mediopago-list')
