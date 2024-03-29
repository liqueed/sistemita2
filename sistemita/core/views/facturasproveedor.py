"""Vistas del modelo FacturaProveedor."""

# Imports
import os

# Datetime
from datetime import date, datetime

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Count, Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView

# Sistemita
from sistemita.core.constants import TIPOS_FACTURA_IMPORT
from sistemita.core.filters import FacturaProveedorFilterSet
from sistemita.core.forms.proveedores import FacturaProveedorForm
from sistemita.core.models.cliente import Factura
from sistemita.core.models.proveedor import (
    FacturaDistribuidaProveedor,
    FacturaProveedor,
)
from sistemita.core.views.home import error_403
from sistemita.utils.commons import get_deleted_objects
from sistemita.utils.export import export_excel, export_retenciones_to_zip
from sistemita.utils.strings import (
    _MESSAGE_SUCCESS_CREATED,
    _MESSAGE_SUCCESS_DELETE,
    _MESSAGE_SUCCESS_UPDATE,
    MESSAGE_403,
)


class FacturaProveedorListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que retorna un lista de facturas a proveedores."""

    filterset_class = FacturaProveedorFilterSet
    paginate_by = 10
    permission_required = 'core.list_facturaproveedor'
    raise_exception = True
    template_name = 'core/facturaproveedor_list.html'

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
        queryset = FacturaProveedor.objects.order_by('-creado')
        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', None)
        try:
            if search:
                queryset = queryset.filter(
                    Q(numero=search)
                    | Q(proveedor__razon_social__icontains=search)
                    | Q(proveedor__cuit__icontains=search)
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
        current_week = date.today().isocalendar()[1]

        # dollar
        nc_dollar = queryset.filter(cobrado=False, moneda='D', tipo__startswith='NC').aggregate(Sum('total'))
        nc_dollar_total = nc_dollar.get('total__sum') if nc_dollar.get('total__sum') else 0
        factura_dollar = (
            queryset.filter(cobrado=False, moneda='D')
            .exclude(tipo__startswith='NC')
            .aggregate(Sum('total'), Count('id'))
        )
        factura_dollar_total = factura_dollar.get('total__sum') if factura_dollar.get('total__sum') else 0
        context['debt_in_dollar'] = {
            'total__sum': factura_dollar_total - nc_dollar_total,
            'id__count': factura_dollar.get('id__count'),
        }

        # peso
        nc_peso = queryset.filter(cobrado=False, moneda='P', tipo__startswith='NC').aggregate(Sum('total'))
        nc_peso_total = nc_peso.get('total__sum') if nc_peso.get('total__sum') else 0
        factura_peso = (
            queryset.filter(cobrado=False, moneda='P')
            .exclude(tipo__startswith='NC')
            .aggregate(Sum('total'), Count('id'))
        )
        factura_peso_total = factura_peso.get('total__sum') if factura_peso.get('total__sum') else 0
        context['debt_in_peso'] = {
            'total__sum': factura_peso_total - nc_peso_total,
            'id__count': factura_peso.get('id__count'),
        }
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
        kwargs['params'] = self.request.GET or None
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

    def get_context_data(self, **kwargs):
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        deletable_objects, model_count, protected = get_deleted_objects([self.object])
        context['deletable_objects'] = deletable_objects
        context['model_count'] = dict(model_count).items()
        context['protected'] = protected
        return context

    def delete(self, request, *args, **kwargs):
        """Método que elimina los archivos relacionados."""
        self.object = self.get_object()
        self.object.archivos.all().delete()
        self.object.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(self.success_url)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaProveedorReportListView(PermissionRequiredMixin, ListView):
    """Vista del reporte de ventas."""

    queryset = Factura.objects.all().order_by('-fecha').filter(facturas_proveedor__isnull=False).distinct()
    paginate_by = 10
    permission_required = 'core.view_report_sales_facturaproveedor'
    raise_exception = True
    template_name = 'core/facturaproveedor_report_list.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')

    def get(self, request, *args, **kwargs):
        """Genera reporte en formato excel."""
        format_list = request.GET.get('formato', False)
        if format_list == 'xls':
            return export_excel(self.request, self.get_queryset())

        return super().get(request, *args, **kwargs)


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
        return redirect('login')


class FacturaProveedorByUserListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que retorna un lista de facturas a proveedores."""

    filterset_class = FacturaProveedorFilterSet
    paginate_by = 10
    permission_required = 'core.view_mis_facturasproveedor'
    raise_exception = True
    template_name = 'core/facturaproveedor_misfacturas.html'

    def get(self, request, *args, **kwargs):
        """Genera reporte en formato excel."""
        format_list = request.GET.get('formato', False)

        if format_list == 'xls':
            return export_excel(self.request, self.get_queryset())

        if format_list == 'pdf':
            seleccionados = self.request.GET.get('seleccionados', None)

            if seleccionados == 'todos':
                response, zip_path = export_retenciones_to_zip(self.request, self.get_queryset())
            else:
                queryset = self.get_queryset().filter(pk__in=seleccionados.split(','))
                response, zip_path = export_retenciones_to_zip(self.request, queryset)

            # Si no hay response es porque no hay retenciones que descargar
            if not response:
                messages.warning(request, 'No hay retenciones disponibles para las facturas seleccionadas.')
                return super().get(request, *args, **kwargs)

            # Remuevo el zip creado
            os.remove(zip_path)
            return response

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Sobreescribe queryset.
        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        user_email = self.request.user.email
        queryset = FacturaProveedor.objects.filter(proveedor__correo=user_email).order_by('-creado')

        search = self.request.GET.get('search', None)
        desde = self.request.GET.get('desde', None)
        hasta = self.request.GET.get('hasta', None)
        order_by = self.request.GET.get('order_by', None)
        try:
            if search:
                queryset = queryset.filter(Q(numero__icontains=search) | Q(total__icontains=search))
            if desde:
                desde = datetime.strptime(desde, '%d/%m/%Y')
                queryset = queryset.filter(fecha__gte=desde)
            if hasta:
                hasta = datetime.strptime(hasta, '%d/%m/%Y')
                queryset = queryset.filter(fecha__lte=hasta)
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


class FacturaProveedorByUserDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una factura a proveedor con retenciones."""

    model = FacturaProveedor
    permission_required = 'core.view_mis_facturasproveedor'
    raise_exception = True
    template_name = 'core/facturaproveedor_user_detail.html'

    def get_object(self, queryset=None):
        """Return the object the view is displaying."""

        user_email = self.request.user.email
        return get_object_or_404(FacturaProveedor, pk=self.kwargs.get('pk'), proveedor__correo=user_email)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaProveedorByUserPendientesListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que retorna un lista de facturas pendientes a facturar."""

    paginate_by = 10
    permission_required = 'core.view_mis_facturasproveedor_pendientes'
    raise_exception = True
    template_name = 'core/facturaproveedor_misfacturas_pendientes.html'

    def get_queryset(self):
        """
        Sobreescribe queryset.
        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        user_email = self.request.user.email
        queryset = FacturaDistribuidaProveedor.objects.filter(
            proveedor__correo=user_email, factura_proveedor__isnull=True
        )
        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', 'factura_distribucion__factura__numero')
        try:
            if search:
                queryset = queryset.filter(Q(numero__icontains=search) | Q(total__icontains=search))
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
