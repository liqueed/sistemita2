"""Vista del modelo Fondo y Costo.

El modelo Fondo está asociado al modelo de factura de cliente.
El modelo Costo está asociado al modelo Fondo.
"""
# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import ListView

# Sistemita
from sistemita.core.utils.strings import MESSAGE_403
from sistemita.core.views.home import error_403
from sistemita.expense.models import Costo, Fondo


class FondoListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que muestra un listado de facturas que constituyen el fondo."""

    paginate_by = 10
    permission_required = 'expense.list_fondo'
    raise_exception = True
    template_name = 'expense/fondo_list.html'

    def get_queryset(self):
        """
        Sobreescribe queryset.
        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = Fondo.objects.order_by('-creado')
        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', None)
        try:
            if search:
                queryset = queryset.filter(
                    Q(numero=search) | Q(cliente__razon_social__icontains=search)
                )
            if order_by:
                queryset = queryset.order_by(order_by)
        except FieldError:
            pass
        return queryset

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        fondo_peso = 0
        for row in queryset.filter(factura__moneda='P', disponible=True):
            fondo_peso += row.factura.porcentaje_fondo_monto

        fondo_dollar = 0
        for row in queryset.filter(factura__moneda='D', disponible=True):
            fondo_dollar += row.factura.porcentaje_fondo_monto

        context['fondo_dollar'] = fondo_dollar
        context['fondo_peso'] = fondo_peso

        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class CostoListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que muestra un listado de costos."""

    paginate_by = 10
    permission_required = 'expense.list_costo'
    raise_exception = True
    template_name = 'expense/costo_list.html'

    def get_queryset(self):
        """
        Sobreescribe queryset.
        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = Costo.objects.order_by('-creado')
        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', None)
        try:
            if search:
                queryset = queryset.filter(
                    Q(numero=search) | Q(cliente__razon_social__icontains=search)
                )
            if order_by:
                queryset = queryset.order_by(order_by)
        except FieldError:
            pass
        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
