"""Vistas del modelo FacturaImpuracion."""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import DeleteView
from django_filters.views import FilterView

# Sistemita
from sistemita.core.filters import FacturaImputadaFilterSet
from sistemita.core.models.cliente import FacturaImputada
from sistemita.core.utils.strings import _MESSAGE_SUCCESS_DELETE, MESSAGE_403
from sistemita.core.views.home import error_403


class FacturaImputadaListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que muestra un listado de facturas imputadas."""

    filterset_class = FacturaImputadaFilterSet
    paginate_by = 10
    permission_required = 'core.list_facturaimputada'
    raise_exception = True
    template_name = 'core/facturaimputada_list.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaImputadaCreateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista para agregar una factura."""

    permission_required = 'core.add_facturaimputada'
    raise_exception = True
    template_name = 'core/facturaimputada_create.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaImputadaDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una factura imputada."""

    model = FacturaImputada
    permission_required = 'core.view_facturaimputada'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaImputadaUpdateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista que modifica una factura imputada."""

    permission_required = 'core.change_facturaimputada'
    raise_exception = True
    template_name = 'core/facturaimputada_update.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaImputadaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina un costo."""

    model = FacturaImputada
    permission_required = 'core.delete_facturaimputada'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_DELETE.format('factura imputada')
    success_url = reverse_lazy('core:facturaimputada-list')
    template_name = 'core/facturaimputada_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        """
        Al eliminar la imputación la factura suma su total y queda como no cobrada.
        """
        self.object = self.get_object()
        # Restablece nota de credito
        nota_de_credito = self.object.nota_de_credito
        nota_de_credito.cobrado = False
        nota_de_credito.total += nota_de_credito.monto_imputado
        nota_de_credito.monto_imputado = 0
        nota_de_credito.save()

        # Restablece facturas
        facturas = self.object.facturas.all()
        for factura in facturas:
            factura.total += factura.monto_imputado
            factura.monto_imputado = 0
            factura.cobrado = False
            factura.save()

        self.object.delete()
        success_url = self.get_success_url()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(success_url)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
