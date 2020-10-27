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

from core.models import FacturaProveedor
from core.filters import FacturaProveedorFilterSet
from core.forms import FacturaProveedorForm
from core.serializers import FacturaProveedorSerializer


class FacturaProveedorViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = FacturaProveedor.objects.all()
    serializer_class = FacturaProveedorSerializer
    permission_classes = (permissions.IsAuthenticated,)


class FacturaProveedorListView(LoginRequiredMixin, FilterView):
    filterset_class = FacturaProveedorFilterSet

    def get_queryset(self):
        queryset = FacturaProveedor.objects.all()
        search = self.request.GET.get('search', None)
        if search:
            self.queryset = queryset.filter(
                Q(proveedor__razon_social__icontains=search) |
                Q(proveedor__correo__icontains=search) |
                Q(proveedor__cuit__icontains=search)
            )

        return self.queryset


class FacturaProveedorAgregarView(LoginRequiredMixin, CreateView):
    model = FacturaProveedor
    form_class = FacturaProveedorForm
    success_url = reverse_lazy('factura-proveedor-listado')


class FacturaProveedorDetalleView(LoginRequiredMixin, DetailView):
    queryset = FacturaProveedor.objects.all()


class FacturaProveedorModificarView(LoginRequiredMixin, UpdateView):
    queryset = FacturaProveedor.objects.all()
    form_class = FacturaProveedorForm
    success_url = reverse_lazy('factura-proveedor-listado')


class FacturaProveedorEliminarView(LoginRequiredMixin, DeleteView):
    queryset = FacturaProveedor.objects.all()
    success_url = reverse_lazy('factura-proveedor-listado')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.archivos.all().delete()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
