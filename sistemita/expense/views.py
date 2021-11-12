"""Vista del modelo Fondo y Costo.

El modelo Fondo está asociado al modelo de factura de cliente.
El modelo Costo está asociado al modelo Fondo.
"""
# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView

# Sistemita
from sistemita.core.utils.export import export_excel
from sistemita.core.utils.strings import (
    MESSAGE_403,
    MESSAGE_SUCCESS_CREATED,
    MESSAGE_SUCCESS_DELETE,
    MESSAGE_SUCCESS_UPDATE,
)
from sistemita.core.views.home import error_403
from sistemita.expense.filters import CostoFilterSet, FondoFilterSet
from sistemita.expense.forms import CostoForm
from sistemita.expense.models import Costo, Fondo


class FondoListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que muestra un listado de facturas que constituyen el fondo."""

    filterset_class = FondoFilterSet
    paginate_by = 10
    permission_required = 'expense.list_fondo'
    raise_exception = True
    template_name = 'expense/fondo_list.html'

    def get(self, request, *args, **kwargs):
        """Genera reporte en formato excel."""
        format_list = request.GET.get('formato', False)
        if format_list == 'xls':
            return export_excel(self.request, self.get_queryset())

        return super().get(request, *args, **kwargs)

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
                    Q(factura__numero__icontains=search) | Q(factura__cliente__razon_social__icontains=search)
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

        context['fondo_dollar'] = round(fondo_dollar, 2)
        context['fondo_peso'] = round(fondo_peso, 2)

        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class CostoListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que muestra un listado de costos."""

    filterset_class = CostoFilterSet
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
                    Q(fondo__factura__numero__icontains=search)
                    | Q(fondo__factura__cliente__razon_social__icontains=search)
                    | Q(descripcion__icontains=search)
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

        costo_peso = 0
        for row in queryset.filter(moneda='P'):
            costo_peso += row.monto

        costo_dollar = 0
        for row in queryset.filter(moneda='D'):
            costo_dollar += row.monto

        context['costo_dollar'] = round(costo_dollar, 2)
        context['costo_peso'] = round(costo_peso, 2)

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
    success_message = MESSAGE_SUCCESS_CREATED.format('costo')
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


class CostoDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina un costo."""

    model = Costo
    permission_required = 'expense.delete_costo'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('costo')
    success_url = reverse_lazy('expense:costo-list')
    template_name = 'expense/costo_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        """
        Al eliminar el costo el fondo queda disponible y se le suma el monto del costo eliminado al
        monto disponible.
        """
        self.object = self.get_object()
        fondo = self.object.fondo
        new_monto_disponible = fondo.monto_disponible + self.object.monto
        self.object.delete()
        Fondo.objects.filter(pk=fondo.pk).update(disponible=True, monto_disponible=new_monto_disponible)

        success_url = self.get_success_url()
        return HttpResponseRedirect(success_url)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
