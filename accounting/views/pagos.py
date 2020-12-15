"""Views de pagos."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView, DetailView, ListView, TemplateView
from django.urls import reverse_lazy

# Django Rest Framework
from rest_framework import mixins, permissions, viewsets

# Accounting
from accounting.models.pago import Pago
from accounting.serializers.pagos import PagoSerializer

# Core
from core.models.proveedor import FacturaProveedor


class PagoViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """Pago view set."""
    serializer_class = PagoSerializer
    queryset = Pago.objects.all()
    permission_classes = (permissions.IsAuthenticated,)


class PagoListView(LoginRequiredMixin, ListView):
    """Lista de pagos"""
    template_name = 'accounting/proveedor_pago_list.html'

    def get_queryset(self):
        queryset = Pago.objects.all().order_by('-creado')
        # Search filter
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(proveedor__razon_social__icontains=search) |
                Q(proveedor__correo__icontains=search) |
                Q(proveedor__cuit__icontains=search)
            )

        return queryset


class PagoAgregarTemplateView(LoginRequiredMixin, TemplateView):
    """Formulario para agregar pagos."""
    template_name = 'accounting/proveedor_pago_form.html'


class PagoEditarTemplateView(LoginRequiredMixin, TemplateView):
    """Formulario para editar pagos."""
    template_name = 'accounting/proveedor_pago_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = kwargs['pk']
        return context


class PagoDetalleView(LoginRequiredMixin, DetailView):
    """Template con los detalle del pago."""
    queryset = Pago.objects.all()


class PagoEliminarView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar pago."""
    queryset = Pago.objects.all()
    success_url = reverse_lazy('accounting:pago-listado')

    def delete(self, request, *args, **kwargs):
        """Sobreescribe método para modificar facturas asociadas."""
        self.object = self.get_object()

        # Las facturas asociadas pasan estar no cobradas
        pago_facturas = self.object.pago_facturas.all()
        for c_factura in pago_facturas:
            FacturaProveedor.objects.filter(pk=c_factura.factura.id).update(
                cobrado=False
            )

        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
