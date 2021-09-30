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
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Sistemita
from sistemita.core.utils.strings import (
    _MESSAGE_SUCCESS_CREATED,
    MESSAGE_403,
    MESSAGE_SUCCESS_UPDATE,
)
from sistemita.core.views.home import error_403
from sistemita.expense.forms import CostoForm
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
                queryset = queryset.filter(Q(numero=search) | Q(cliente__razon_social__icontains=search))
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
                queryset = queryset.filter(Q(numero=search) | Q(cliente__razon_social__icontains=search))
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
        for row in queryset.filter(fondo__moneda='P'):
            fondo_peso += row.monto

        fondo_dollar = 0
        for row in queryset.filter(fondo__moneda='D'):
            fondo_dollar += row.monto

        context['fondo_dollar'] = fondo_dollar
        context['fondo_peso'] = fondo_peso

        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class CostoCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista para agregar un costo."""

    form_class = CostoForm
    model = Costo
    permission_required = 'expense.add_costo'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_CREATED.format('costo')
    template_name = 'expense/costo_form.html'

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('expense.change_costo'):
            return reverse('expense:costo-update', args=(self.object.id,))
        if self.request.user.has_perm('expense.view_costo'):
            return reverse('expense:costo-detail', args=(self.object.id,))
        if self.request.user.has_perm('expense.list_costo'):
            return reverse('expense:costo-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class CostoDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de un costo."""

    model = Costo
    permission_required = 'expense.view_costo'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class CostoUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un costo."""

    form_class = CostoForm
    model = Costo
    permission_required = 'expense.change_costo'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_UPDATE.format('costo')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('expense:costo-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
