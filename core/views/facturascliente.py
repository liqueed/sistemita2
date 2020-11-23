from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django_filters.views import FilterView

from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

from core.models.cliente import Factura
from core.forms import FacturaForm
from core.serializers import FacturaSerializer
from core.filters import FacturaFilterSet


class FacturaViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = (permissions.IsAuthenticated,)


class FacturaEliminarView(LoginRequiredMixin, DeleteView):
    queryset = Factura.objects.all()
    success_url = reverse_lazy('factura-listado')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
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
