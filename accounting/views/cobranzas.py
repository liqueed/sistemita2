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
from core.utils.strings import _MESSAGE_SUCCESS_DELETE, MESSAGE_403

# Views
from core.views.home import error_403


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

    def get_queryset(self):
        """Devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Cobranza.objects.order_by('id')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(cliente__razon_social__icontains=search) | Q(cliente__correo__icontains=search) |
                Q(cliente__cuit__icontains=search)
            )

        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class CobranzaCreateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista que devuelve un formulario para agregar una cobranza."""

    permission_required = 'accounting.add_cobranza'
    raise_exception = True
    template_name = 'accounting/cobranza_create.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class CobranzaDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra los deltalle de una cobranza."""

    model = Cobranza
    permission_required = 'accounting.view_cobranza'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


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
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)


class CobranzaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar una cobranza."""

    model = Cobranza
    permission_required = 'accounting.delete_cobranza'
    raise_exception = True
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

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos."""
        if self.raise_exception:
            return error_403(self.request, MESSAGE_403)
