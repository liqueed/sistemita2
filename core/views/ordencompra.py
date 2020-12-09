from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

from core.models.cliente import OrdenCompra
from core.forms import OrdenCompraForm


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
    template_name = 'ordendecompra-list'

    def get_queryset(self):
        queryset = OrdenCompra.objects.all()
        # Search filter
        search = self.request.GET.get('search', None)
        if search:
            # self.queryset = self.queryset.annotate(
            #     search=SearchVector('last_name') + SearchVector('first_name') + SearchVector('email') + SearchVector('username'),
            # ).filter(search=search)
            queryset = queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search) | Q(cuit__icontains=search)
            )

        return queryset
