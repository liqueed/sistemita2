"""Vistas del modelo FacturaProveedor."""

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView

# Sistemita
from sistemita.core.constants import TIPOS_FACTURA_IMPORT
from sistemita.core.filters import FacturaProveedorFilterSet
from sistemita.core.forms.proveedores import FacturaProveedorForm
from sistemita.core.models.cliente import Factura
from sistemita.core.models.proveedor import FacturaProveedor
from sistemita.core.utils.export import export_excel
from sistemita.core.utils.strings import (
    _MESSAGE_SUCCESS_CREATED,
    _MESSAGE_SUCCESS_DELETE,
    _MESSAGE_SUCCESS_UPDATE,
    MESSAGE_403,
)
from sistemita.core.views.home import error_403


class FacturaProveedorListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que retorna un lista de facturas a proveedores."""

    model = FacturaProveedor
    filterset_class = FacturaProveedorFilterSet
    permission_required = 'core.list_facturaproveedor'
    raise_exception = True
    template_name = 'core/facturaproveedor_list.html'
    ordering = ['-creado']

    def get(self, request, *args, **kwargs):
        """Genera reporte en formato excel."""
        format_list = request.GET.get('formato', False)

        if format_list == 'xls':
            return export_excel(self.request, self.get_queryset())

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        current_week = date.today().isocalendar()[1]

        context['debt_in_dollar'] = queryset.filter(cobrado=False, moneda='D').aggregate(Sum('total'), Count('id'))
        context['debt_in_peso'] = queryset.filter(cobrado=False, moneda='P').aggregate(Sum('total'), Count('id'))
        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaProveedorCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que create un factura a proveedor."""

    form_class = FacturaProveedorForm
    model = FacturaProveedor
    permission_required = 'core.add_facturaproveedor'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_CREATED.format('factura a proveedor')

    def get_form_kwargs(self):
        """Envía parámetros extras al formulario."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_facturaproveedor'):
            return reverse('core:facturaproveedor-update', args=(self.object.id,))
        if self.request.user.has_perm('core.view_facturaproveedor'):
            return reverse('core:facturaproveedor-detail', args=(self.object.id,))
        if self.request.user.has_perm('core.list_facturaproveedor'):
            return reverse('core:facturaproveedor-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaProveedorDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una factura a proveedor."""

    model = FacturaProveedor
    permission_required = 'core.view_facturaproveedor'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaProveedorUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica la factura a proveedor."""

    form_class = FacturaProveedorForm
    model = FacturaProveedor
    permission_required = 'core.change_facturaproveedor'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_UPDATE.format('factura a proveedor')

    def get_form_kwargs(self):
        """Envía parámetros extras al formulario."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('core:facturaproveedor-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaProveedorDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina una factura a proveedor."""

    model = FacturaProveedor
    permission_required = 'core.delete_facturaproveedor'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_DELETE.format('factura a proveedor')
    success_url = reverse_lazy('core:facturaproveedor-list')

    def delete(self, request, *args, **kwargs):
        """Método que elimina los archivos relacionados."""
        factura = self.get_object()
        factura.archivos.all().delete()
        factura.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(self.success_url)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return super().handle_no_permission()


class FacturaProveedorReportListView(PermissionRequiredMixin, ListView):
    """Vista del reporte de ventas."""

    queryset = Factura.objects.all().order_by('-fecha').filter(facturas_proveedor__isnull=False).distinct()
    permission_required = 'core.view_report_sales_facturaproveedor'
    raise_exception = True
    template_name = 'core/facturaproveedor_report_list.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return super().handle_no_permission()

    def get(self, request, *args, **kwargs):
        """Genera reporte en formato excel."""
        format_list = request.GET.get('formato', False)
        if format_list == 'xls':
            return export_excel(self.request, self.get_queryset())

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = FacturaProveedor.objects.all()
        current_week = date.today().isocalendar()[1]

        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context


class FacturaProveedorImportTemplateView(PermissionRequiredMixin, TemplateView):
    """Template para importar facturas."""

    model = FacturaProveedor
    permission_required = 'core.add_facturaproveedor'
    raise_exception = True
    template_name = 'core/facturaproveedor_import.html'

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.
        Pass response_kwargs to the constructor of the response class.
        """
        context['tipo_facturas'] = list(f[0] for f in TIPOS_FACTURA_IMPORT)
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return super().handle_no_permission()
