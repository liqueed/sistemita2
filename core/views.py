from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from rest_framework import permissions
from rest_framework import viewsets

from authorization.models import User
from core.forms import ClienteForm, ProveedorForm
from core.models import Cliente, Distrito, Localidad, Proveedor
from core.serializers import DistritoSerializer, LocalidadSerializer


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
