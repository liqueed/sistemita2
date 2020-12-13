from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

from core.models.proveedor import Proveedor
from core.forms import ProveedorForm
from core.serializers import ProveedorSerializer


class ProveedorViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ProveedorEliminarView(LoginRequiredMixin, DeleteView):
    queryset = Proveedor.objects.all()
    success_url = reverse_lazy('proveedor-listado')


class ProveedorDetalleView(LoginRequiredMixin, DetailView):
    queryset = Proveedor.objects.all()


class ProveedorModificarView(LoginRequiredMixin, UpdateView):
    queryset = Proveedor.objects.all()
    form_class = ProveedorForm
    success_url = reverse_lazy('proveedor-listado')


class ProveedorAgregarView(LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    success_url = reverse_lazy('proveedor-listado')


class ProveedorListView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        queryset = Proveedor.objects.all()
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search) | Q(cuit__icontains=search)
            )
        return queryset
