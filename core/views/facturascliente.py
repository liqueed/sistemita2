"""Vistas del módulo facturación a clientes."""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django_filters.views import FilterView

# Django REST Framework
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

# Models
from core.models.cliente import Factura
from accounting.models.cobranza import Cobranza, CobranzaFactura

# Forms
from core.forms import FacturaForm

# Serializer
from core.serializers import FacturaSerializer

# Filters
from core.filters import FacturaFilterSet


class FacturaViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """Factura view set."""

    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_fields = ('cliente', 'cobrado')


class FacturaListView(PermissionRequiredMixin, FilterView):
    """Vista que muestra un listado de facturas."""

    filterset_class = FacturaFilterSet
    permission_required = 'core.list_factura'

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


class FacturaCreateView(PermissionRequiredMixin, CreateView):
    """Vista para agregar una factura."""

    model = Factura
    form_class = FacturaForm
    permission_required = 'core.add_factura'
    success_url = reverse_lazy('factura-list')


class FacturaDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra el detalle de una factura."""

    queryset = Factura.objects.all()
    permission_required = 'core.view_factura'


class FacturaUpdateView(PermissionRequiredMixin, UpdateView):
    """Vista que modifica un factura."""

    queryset = Factura.objects.all()
    form_class = FacturaForm
    permission_required = 'core.change_factura'
    success_url = reverse_lazy('factura-list')


class FacturaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina una factura."""

    queryset = Factura.objects.all()
    permission_required = 'core.delete_factura'
    success_url = reverse_lazy('factura-list')

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
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
