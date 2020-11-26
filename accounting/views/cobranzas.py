"""Cobranza vistas."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, TemplateView

# Models
from accounting.models.cobranza import Cobranza


class CobranzaListView(LoginRequiredMixin, ListView):
    """Lista de cobranzas"""
    template_name = 'accounting/cliente_cobranza_list.html'

    def get_queryset(self):
        queryset = Cobranza.objects.all()
        # Search filter
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search) | Q(cuit__icontains=search)
            )

        return queryset


class CobranzaAgregarTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'accounting/cliente_cobranza_form.html'
