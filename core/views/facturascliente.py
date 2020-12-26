"""Vistas del modelo Factura.

El modelo Factura está asociado al modelo cliente.
"""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django_filters.views import FilterView
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView

# Django REST Framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

# Models
from core.models.cliente import Factura
from accounting.models.cobranza import Cobranza, CobranzaFactura

# Forms
from core.forms.clientes import FacturaForm

# Serializer
from core.serializers import FacturaSerializer

# Filters
from core.filters import FacturaFilterSet

# Utils
from core.utils.strings import (
    _MESSAGE_SUCCESS_CREATED, _MESSAGE_SUCCESS_UPDATE, _MESSAGE_SUCCESS_DELETE
)


class FacturaViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """Factura view set."""

    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_fields = ('cliente', 'cobrado')


class FacturaListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que muestra un listado de facturas."""

    filterset_class = FacturaFilterSet
    paginate_by = 10
    permission_required = 'core.list_factura'
    template_name = 'core/facturacliente_list.html'

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = Factura.objects.all()
        search = self.request.GET.get('search', None)
        if search:
            self.queryset = queryset.filter(
                Q(cliente__razon_social__icontains=search) |
                Q(cliente__correo__icontains=search) |
                Q(cliente__cuit__icontains=search)
            )

        return self.queryset


class FacturaCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista para agregar una factura."""

    model = Factura
    form_class = FacturaForm
    permission_required = 'core.add_factura'
    success_message = _MESSAGE_SUCCESS_CREATED.format('factura del cliente')
    template_name = 'core/facturacliente_form.html'

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_factura'):
            return reverse('factura-update', args=(self.object.id,))
        elif self.request.user.has_perm('core.view_factura'):
            return reverse('factura-detail', args=(self.object.id,))
        elif self.request.user.has_perm('core.list_factura'):
            return reverse('factura-list')
        else:
            return reverse('home')


class FacturaDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una factura."""

    model = Factura
    permission_required = 'core.view_factura'
    template_name = 'core/facturacliente_detail.html'


class FacturaUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un factura."""

    model = Factura
    form_class = FacturaForm
    permission_required = 'core.change_factura'
    success_message = _MESSAGE_SUCCESS_UPDATE.format('factura del cliente')
    template_name = 'core/facturacliente_form.html'

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('factura-update', args=(self.object.id,))


class FacturaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina una factura."""

    model = Factura
    permission_required = 'core.delete_factura'
    success_message = _MESSAGE_SUCCESS_DELETE.format('factura del cliente')
    success_url = reverse_lazy('factura-list')
    template_name = 'core/facturacliente_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        """Sobreescribe método para eliminar una factura.

        Si elimino una factura y está asociada a una cobranza que la tiene por única
        factura, elimino la cobranza.
        """
        self.object = self.get_object()

        cobranza_factura = CobranzaFactura.objects.filter(factura=self.object).first()
        if cobranza_factura:
            count = cobranza_factura.cobranza.cobranza_facturas.count()
            if count == 1:
                Cobranza.objects.get(pk=cobranza_factura.cobranza.pk).delete()

        self.object.archivos.all().delete()
        self.object.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(self.success_url)
