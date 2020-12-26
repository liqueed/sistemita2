"""Vistas del modelo de Pago."""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, TemplateView

# Django Rest Framework
from rest_framework import mixins, permissions, viewsets

# Accounting
from accounting.models.pago import Pago
from accounting.serializers.pagos import PagoSerializer

# Core
from core.models.proveedor import FacturaProveedor

# Utils
from core.utils.strings import MESSAGE_SUCCESS_DELETE


class PagoViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """Pago view set."""

    serializer_class = PagoSerializer
    queryset = Pago.objects.all()
    permission_classes = (permissions.IsAuthenticated,)


class PagoListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que devuelve un listado de pagos."""

    paginate_by = 10
    permission_required = 'accounting.list_pago'

    def get_queryset(self):
        """Modifica el orden y devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Pago.objects.order_by('id')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(proveedor__razon_social__icontains=search) |
                Q(proveedor__correo__icontains=search) |
                Q(proveedor__cuit__icontains=search)
            )

        return queryset


class PagoCreateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista que muestra un formulario para agregar un pago."""

    permission_required = 'accounting.add_pago'
    template_name = 'accounting/pago_create.html'


class PagoDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra los detalles de un pago."""

    model = Pago
    permission_required = 'accounting.view_pago'


class PagoUpdateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista para editar una cobranza."""

    permission_required = 'accounting.change_pago'
    template_name = 'accounting/pago_update.html'

    def get_context_data(self, **kwargs):
        """Envía al template la clave primaria."""
        context = super().get_context_data(**kwargs)
        context['pk'] = kwargs['pk']
        return context


class PagoDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar un pago."""

    model = Pago
    permission_required = 'accounting.delete_pago'
    success_message = MESSAGE_SUCCESS_DELETE.format('pago')
    success_url = reverse_lazy('accounting:pago-list')

    def delete(self, request, *args, **kwargs):
        """Modifica el estado de las facturas que son desasociadas del pago al eliminarse."""
        self.object = self.get_object()

        pago_facturas = self.object.pago_facturas.all()
        for c_factura in pago_facturas:
            FacturaProveedor.objects.filter(pk=c_factura.factura.id).update(
                cobrado=False
            )

        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(success_url)
