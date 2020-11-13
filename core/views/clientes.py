from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets

from core.models import Cliente
from core.forms import ClienteForm
from core.serializers import ClienteSerializer


class ClienteViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = (permissions.IsAuthenticated,)


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
    template_name = 'core/cliente_list.html'

    def get_queryset(self):
        self.queryset = Cliente.objects.all()
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
