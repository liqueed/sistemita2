"""Cobranza vistas."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DeleteView, ListView, TemplateView
from django.urls import reverse_lazy

# Django Rest Framework
from rest_framework import permissions
from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response

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
        queryset = Cobranza.objects.all()
        # Search filter
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search)
                | Q(cuit__icontains=search)
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


class CobranzaEliminarView(LoginRequiredMixin, DeleteView):
    queryset = Cobranza.objects.all()
    success_url = reverse_lazy('accounting:cobranza-listado')
