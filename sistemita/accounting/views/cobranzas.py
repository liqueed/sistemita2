"""Vistas del modelo de Cobranza."""

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, TemplateView

# Django Rest Framework
from rest_framework import mixins, permissions, viewsets

# Accounting
from sistemita.accounting.models.cobranza import Cobranza
from sistemita.accounting.serializers.cobranzas import CobranzaSerializer

# Core
from sistemita.core.models.cliente import Factura
from sistemita.core.utils.strings import _MESSAGE_SUCCESS_DELETE, MESSAGE_403
from sistemita.core.views.home import error_403


class CobranzaViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Cobranza view set."""

    queryset = Cobranza.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CobranzaSerializer


class CobranzaListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que devuelve un listado de cobranzas."""

    paginate_by = 10
    permission_required = 'accounting.list_cobranza'
    raise_exception = True

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        current_week = date.today().isocalendar()[1]

        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context

    def get_queryset(self):
        """Devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Cobranza.objects.order_by('-fecha')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(cliente__razon_social__icontains=search) | Q(cliente__correo__icontains=search) |
                Q(cliente__cuit__icontains=search)
            )

        return queryset

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
            Factura.objects.filter(pk=c_factura.factura.id).update(
                cobrado=False
            )

        success_url = self.get_success_url()
        cobranza.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(success_url)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
