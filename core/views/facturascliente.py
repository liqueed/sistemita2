"""Cliente views."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
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
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_fields = ('cliente', 'cobrado')


class FacturaEliminarView(LoginRequiredMixin, DeleteView):
    queryset = Factura.objects.all()
    success_url = reverse_lazy('factura-listado')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Si elimino una factura y está asociada a una cobranza que la tiene por única
        # factura, elimino la cobranza
        cobranza_factura = CobranzaFactura.objects.filter(factura=self.object).first()
        if cobranza_factura:
            count = cobranza_factura.cobranza.cobranza_facturas.count()
            if count == 1:
                Cobranza.objects.get(pk=cobranza_factura.cobranza.pk).delete()

        self.object.archivos.all().delete()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class FacturaDetalleView(LoginRequiredMixin, DetailView):
    queryset = Factura.objects.all()


class FacturaModificarView(LoginRequiredMixin, UpdateView):
    queryset = Factura.objects.all()
    form_class = FacturaForm
    success_url = reverse_lazy('factura-listado')


class FacturaAgregarView(LoginRequiredMixin, CreateView):
    model = Factura
    form_class = FacturaForm
    success_url = reverse_lazy('factura-listado')


class FacturaListView(LoginRequiredMixin, FilterView):
    filterset_class = FacturaFilterSet

    def get_queryset(self):
        # Search filter
        queryset = Factura.objects.all()
        search = self.request.GET.get('search', None)
        if search:
            self.queryset = queryset.filter(
                Q(cliente__razon_social__icontains=search) | Q(cliente__correo__icontains=search) | Q(cliente__cuit__icontains=search)
            )

        return self.queryset
