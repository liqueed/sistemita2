"""Vistas del modelo MedioPago."""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse, reverse_lazy

# Django REST Framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

# Forms
from core.forms.mediospago import MedioPagoForm

# Models
from core.models.mediopago import MedioPago

# Serializers
from core.serializers import MedioPagoSerializer

from core.utils.strings import (
    MESSAGE_SUCCESS_CREATED, MESSAGE_SUCCESS_UPDATE, MESSAGE_SUCCESS_DELETE
)


class MedioPagoViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """Medio de pago view set."""

    queryset = MedioPago.objects.all()
    serializer_class = MedioPagoSerializer
    permission_classes = (permissions.IsAuthenticated,)


class MedioPagoListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que retorna un listado con los medios de pagos."""

    paginate_by = 10
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


class MedioPagoCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que agrega un medio de pago."""

    model = MedioPago
    form_class = MedioPagoForm
    permission_required = 'core.add_mediopago'
    success_message = MESSAGE_SUCCESS_CREATED.format('medio de pago')

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_mediopago'):
            return reverse('mediopago-update', args=(self.object.id,))
        elif self.request.user.has_perm('core.view_mediopago'):
            return reverse('mediopago-detail', args=(self.object.id,))
        elif self.request.user.has_perm('core.list_mediopago'):
            return reverse('mediopago-list')
        else:
            return reverse('home')


class MedioPagoDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detall de un medio de pago."""

    model = MedioPago
    permission_required = 'core.view_mediopago'


class MedioPagoUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un medio de pago."""

    model = MedioPago
    form_class = MedioPagoForm
    permission_required = 'core.change_mediopago'
    success_message = MESSAGE_SUCCESS_UPDATE.format('medio de pago')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('mediopago-update', args=(self.object.id,))


class MedioPagoDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina un medio de pago."""

    model = MedioPago
    permission_required = 'core.delete_mediopago'
    success_message = MESSAGE_SUCCESS_DELETE.format('medio de pago')
    success_url = reverse_lazy('mediopago-list')

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super(MedioPagoDeleteView, self).delete(request, *args, **kwargs)
