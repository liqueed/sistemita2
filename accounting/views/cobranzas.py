"""Vistas del módulo de cobranza."""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView, DetailView, ListView, TemplateView
from django.urls import reverse_lazy

# Django Rest Framework
from rest_framework import mixins, permissions, viewsets

# Accounting
from accounting.models.cobranza import Cobranza
from accounting.serializers.cobranzas import CobranzaSerializer

# Core
from core.models.cliente import Factura


class CobranzaViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Cobranza view set."""

    serializer_class = CobranzaSerializer
    queryset = Cobranza.objects.all()
    permission_classes = (permissions.IsAuthenticated,)


class CobranzaListView(PermissionRequiredMixin, ListView):
    """Vista que devuelve un listado de cobranzas."""

    template_name = 'accounting/cliente_cobranza_list.html'
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
    """Formulario para agregar cobranzas."""

    template_name = 'accounting/cliente_cobranza_form.html'
    permission_required = 'accounting.add_cobranza'


class CobranzaUpdateTemplateView(PermissionRequiredMixin, TemplateView):
    """Formulario para editar cobranzas."""

    template_name = 'accounting/cliente_cobranza_edit.html'
    permission_required = 'accounting.change_cobranza'

    def get_context_data(self, **kwargs):
        """Envía la clave primaria como contexto al template."""
        context = super().get_context_data(**kwargs)
        context['pk'] = kwargs['pk']
        return context


class CobranzaDetailView(PermissionRequiredMixin, DetailView):
    """Vista con los detalles de una cobranza."""

    queryset = Cobranza.objects.all()
    permission_required = 'accounting.detail_cobranza'


class CobranzaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar una cobranza."""

    queryset = Cobranza.objects.all()
    success_url = reverse_lazy('accounting:cobranza-list')
    permission_required = 'accounting.delete_cobranza'

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
        return HttpResponseRedirect(success_url)
