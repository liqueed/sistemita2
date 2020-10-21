from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

from authorization.models import User
from core.filters import FacturaFilterSet
from core.forms import ClienteForm, FacturaForm, MedioPagoForm, ProveedorForm, OrdenCompraForm
from core.models import Archivo, Cliente, Distrito, Factura, Localidad, MedioPago, Proveedor, OrdenCompra
from core.serializers import ArchivoSerializer, ClienteSerializer, DistritoSerializer, FacturaSerializer, \
    LocalidadSerializer


class ArchivoViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Archivo.objects.all()
    serializer_class = ArchivoSerializer
    permission_classes = (permissions.IsAuthenticated,)


class MedioPagoListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        # Search filter
        queryset = MedioPago.objects.all()
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                nombre__icontains=search
            )
        return queryset


class MedioPagoAgregarView(LoginRequiredMixin, CreateView):
    model = MedioPago
    form_class = MedioPagoForm
    success_url = reverse_lazy('mediopago-listado')


class MedioPagoDetalleView(LoginRequiredMixin, DetailView):
    queryset = MedioPago.objects.all()


class MedioPagoModificarView(LoginRequiredMixin, UpdateView):
    queryset = MedioPago.objects.all()
    form_class = MedioPagoForm
    success_url = reverse_lazy('mediopago-listado')


class MedioPagoEliminarView(LoginRequiredMixin, DeleteView):
    queryset = MedioPago.objects.all()
    success_url = reverse_lazy('mediopago-listado')


class OrdenCompraEliminarView(LoginRequiredMixin, DeleteView):
    queryset = OrdenCompra.objects.all()
    success_url = reverse_lazy('factura-listado')


class OrdenCompraDetalleView(LoginRequiredMixin, DetailView):
    queryset = OrdenCompra.objects.all()


class OrdenCompraModificarView(LoginRequiredMixin, UpdateView):
    queryset = OrdenCompra.objects.all()
    form_class = OrdenCompraForm
    success_url = reverse_lazy('ordencompra-listado')


class OrdenCompraAgregarView(LoginRequiredMixin, CreateView):
    model = OrdenCompra
    form_class = OrdenCompraForm
    success_url = reverse_lazy('ordencompra-listado')


class OrdenCompraListView(LoginRequiredMixin, ListView):
    queryset = OrdenCompra.objects.all()

    def get_queryset(self):
        # Search filter
        search = self.request.GET.get('search', None)
        if search:
            # self.queryset = self.queryset.annotate(
            #     search=SearchVector('last_name') + SearchVector('first_name') + SearchVector('email') + SearchVector('username'),
            # ).filter(search=search)
            self.queryset = self.queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search) | Q(cuit__icontains=search)
            )

        return self.queryset


class ClienteViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = (permissions.IsAuthenticated,)


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
    queryset = Proveedor.objects.all()

    def get_queryset(self):
        # Search filter
        search = self.request.GET.get('search', None)
        if search:
            # self.queryset = self.queryset.annotate(
            #     search=SearchVector('last_name') + SearchVector('first_name') + SearchVector('email') + SearchVector('username'),
            # ).filter(search=search)
            self.queryset = self.queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search) | Q(cuit__icontains=search)
            )

        return self.queryset


class LocalidadViewSet(viewsets.ModelViewSet):
    queryset = Localidad.objects.all()
    serializer_class = LocalidadSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('distrito',)


class DistritoViewSet(viewsets.ModelViewSet):
    queryset = Distrito.objects.all()
    serializer_class = DistritoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ('provincia',)


class ClienteEliminarView(LoginRequiredMixin, DeleteView):
    queryset = Cliente.objects.all()
    success_url = reverse_lazy('cliente-listado')


class ClienteDetalleView(LoginRequiredMixin, DetailView):
    queryset = Cliente.objects.all()


class ClienteModificarView(LoginRequiredMixin, UpdateView):
    queryset = Cliente.objects.all()
    form_class = ClienteForm
    success_url = reverse_lazy('cliente-listado')


class ClienteAgregarView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    success_url = reverse_lazy('cliente-listado')


class ClienteListView(LoginRequiredMixin, ListView):
    queryset = Cliente.objects.all()

    def get_queryset(self):
        # Search filter
        search = self.request.GET.get('search', None)
        if search:
            # self.queryset = self.queryset.annotate(
            #     search=SearchVector('last_name') + SearchVector('first_name') + SearchVector('email') + SearchVector('username'),
            # ).filter(search=search)
            self.queryset = self.queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search) | Q(cuit__icontains=search)
            )

        return self.queryset


class UsuarioListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'core/user_list.html'
    queryset = User.objects.order_by('username')

    def get_queryset(self):
        # Search filter
        search = self.request.GET.get('search', None)
        if search:
            # self.queryset = self.queryset.annotate(
            #     search=SearchVector('last_name') + SearchVector('first_name') + SearchVector('email') + SearchVector('username'),
            # ).filter(search=search)
            self.queryset = self.queryset.filter(username__search=search)

        return self.queryset


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'
