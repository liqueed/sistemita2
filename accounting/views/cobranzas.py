"""Cobranza vistas."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView, DetailView, ListView, TemplateView
from django.urls import reverse_lazy
# Django Rest Framework
from rest_framework import permissions
from rest_framework import mixins, status
from rest_framework import viewsets

# Models
from accounting.models.cobranza import Cobranza

# Serializers
from accounting.serializers import CobranzaSerializer


class CobranzaViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Cobranza view set."""
    serializer_class = CobranzaSerializer
    queryset = Cobranza.objects.all()
    permission_classes = (permissions.AllowAny,)  # TODO: Only test


class CobranzaListView(LoginRequiredMixin, ListView):
    """Lista de cobranzas"""
    template_name = 'accounting/cliente_cobranza_list.html'

    def get_queryset(self):
        queryset = Cobranza.objects.all().order_by('-creado')
        # Search filter
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(cliente__razon_social__icontains=search) |
                Q(cliente__correo__icontains=search) |
                Q(cliente__cuit__icontains=search)
            )

        return queryset


class CobranzaAgregarTemplateView(LoginRequiredMixin, TemplateView):
    """Formulario para agregar cobranzas."""
    template_name = 'accounting/cliente_cobranza_form.html'


class CobranzaEditarTemplateView(LoginRequiredMixin, TemplateView):
    """Formulario para editar cobranzas."""
    template_name = 'accounting/cliente_cobranza_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = kwargs['pk']
        return context


class CobranzaDetalleView(LoginRequiredMixin, DetailView):
    """Template con los detalle de la cobranza."""
    queryset = Cobranza.objects.all()


class CobranzaEliminarView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar cobranza."""
    queryset = Cobranza.objects.all()
    success_url = reverse_lazy('accounting:cobranza-listado')

    def delete(self, request, *args, **kwargs):
        """Sobreescribe método para modificar facturas asociadas."""
        self.object = self.get_object()

        # Las facturas asociadas pasan estar no cobradas
        cobranza_facturas = self.object.cobranza_facturas.all()
        for c_factura in cobranza_facturas:
            factura = c_factura.factura
            factura.cobrado = False
            factura.save()

        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
