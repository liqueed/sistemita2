"""Vistas del modelo de Cobranza."""

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, TemplateView
from django_filters.views import FilterView

# Sistemita
from sistemita.accounting.filters import CobranzaFilterSet
from sistemita.accounting.models.cobranza import Cobranza
from sistemita.core.models.cliente import Factura
from sistemita.core.utils.strings import _MESSAGE_SUCCESS_DELETE, MESSAGE_403
from sistemita.core.views.home import error_403


class CobranzaListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que devuelve un listado de cobranzas."""

    model = Cobranza
    filterset_class = CobranzaFilterSet
    permission_required = 'accounting.list_cobranza'
    raise_exception = True
    template_name = 'accounting/cobranza_list.html'
    ordering = ['-creado']

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        current_week = date.today().isocalendar()[1]

        context['count'] = queryset.count()
        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class CobranzaCreateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista que devuelve un formulario para agregar una cobranza."""

    permission_required = 'accounting.add_cobranza'
    raise_exception = True
    template_name = 'accounting/cobranza_create.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class CobranzaDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra los deltalle de una cobranza."""

    model = Cobranza
    permission_required = 'accounting.view_cobranza'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class CobranzaUpdateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista para editar una cobranza."""

    permission_required = 'accounting.change_cobranza'
    raise_exception = True
    template_name = 'accounting/cobranza_update.html'

    def get_context_data(self, **kwargs):
        """Envía la clave primaria como contexto al template."""
        context = super().get_context_data(**kwargs)
        context['pk'] = kwargs['pk']
        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class CobranzaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar una cobranza."""

    model = Cobranza
    permission_required = 'accounting.delete_cobranza'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_DELETE.format('cobranza')
    success_url = reverse_lazy('accounting:cobranza-list')

    def delete(self, request, *args, **kwargs):
        """Sobreescribe método para modificar facturas asociadas."""
        cobranza = self.get_object()

        # Las facturas asociadas pasan estar no cobradas
        cobranza_facturas = cobranza.cobranza_facturas.all()
        for c_factura in cobranza_facturas:
            Factura.objects.filter(pk=c_factura.factura.id).update(cobrado=False)

        success_url = self.get_success_url()
        cobranza.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(success_url)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
