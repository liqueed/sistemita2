"""Vistas del modelo de Cobranza."""

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
from accounting.models.cobranza import Cobranza
from accounting.serializers.cobranzas import CobranzaSerializer

# Core
from core.models.cliente import Factura

# Utils
from core.utils.strings import _MESSAGE_SUCCESS_DELETE


class CobranzaViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Cobranza view set."""

    queryset = Cobranza.objects.all()
    serializer_class = CobranzaSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CobranzaListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que devuelve un listado de cobranzas."""

    permission_required = 'accounting.list_cobranza'

    def get_queryset(self):
        """Devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Cobranza.objects.all().order_by('-creado')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(cliente__razon_social__icontains=search) |
                Q(cliente__correo__icontains=search) |
                Q(cliente__cuit__icontains=search)
            )

        return queryset


class CobranzaCreateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista que devuelve un formulario para agregar una cobranza."""

    permission_required = 'accounting.add_cobranza'
    template_name = 'accounting/cobranza_create.html'


class CobranzaDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra los deltalle de una cobranza."""

    model = Cobranza
    permission_required = 'accounting.view_cobranza'


class CobranzaUpdateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista para editar una cobranza."""

    permission_required = 'accounting.change_cobranza'
    template_name = 'accounting/cobranza_update.html'

    def get_context_data(self, **kwargs):
        """Envía la clave primaria como contexto al template."""
        context = super().get_context_data(**kwargs)
        context['pk'] = kwargs['pk']
        return context


class CobranzaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar una cobranza."""

    model = Cobranza
    permission_required = 'accounting.delete_cobranza'
    success_message = _MESSAGE_SUCCESS_DELETE.format('cobranza')
    success_url = reverse_lazy('accounting:cobranza-list')

    def delete(self, request, *args, **kwargs):
        """Sobreescribe método para modificar facturas asociadas."""
        self.object = self.get_object()

        # Las facturas asociadas pasan estar no cobradas
        cobranza_facturas = self.object.cobranza_facturas.all()
        for c_factura in cobranza_facturas:
            Factura.objects.filter(pk=c_factura.factura.id).update(
                cobrado=False
            )

        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(success_url)
