"""Vistas del modelo Factura.

El modelo Factura está asociado al modelo cliente.
"""
# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Count, Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView

# Sistemita
from sistemita.accounting.models.cobranza import Cobranza, CobranzaFactura
from sistemita.core.constants import TIPOS_FACTURA_IMPORT
from sistemita.core.filters import FacturaFilterSet
from sistemita.core.forms.clientes import FacturaForm
from sistemita.core.models.cliente import Factura
from sistemita.core.views.home import error_403
from sistemita.utils.commons import get_deleted_objects
from sistemita.utils.export import export_excel
from sistemita.utils.strings import (
    _MESSAGE_SUCCESS_CREATED,
    _MESSAGE_SUCCESS_DELETE,
    _MESSAGE_SUCCESS_UPDATE,
    MESSAGE_403,
)


class FacturaListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que muestra un listado de facturas."""

    filterset_class = FacturaFilterSet
    paginate_by = 10
    permission_required = 'core.list_factura'
    raise_exception = True
    template_name = 'core/facturacliente_list.html'

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
        queryset = Factura.objects.order_by('-creado')
        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', None)
        try:
            if search:
                queryset = queryset.filter(
                    Q(numero__icontains=search)
                    | Q(cliente__razon_social__icontains=search)
                    | Q(cliente__cuit__icontains=search)
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


class FacturaCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista para agregar una factura."""

    form_class = FacturaForm
    model = Factura
    permission_required = 'core.add_factura'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_CREATED.format('factura del cliente')
    template_name = 'core/facturacliente_form.html'

    def get_form_kwargs(self):
        """Envía parámetros extras al formulario."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_factura'):
            return reverse('core:factura-update', args=(self.object.id,))
        if self.request.user.has_perm('core.view_factura'):
            return reverse('core:factura-detail', args=(self.object.id,))
        if self.request.user.has_perm('core.list_factura'):
            return reverse('core:factura-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una factura."""

    model = Factura
    permission_required = 'core.view_factura'
    raise_exception = True
    template_name = 'core/facturacliente_detail.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un factura."""

    form_class = FacturaForm
    model = Factura
    permission_required = 'core.change_factura'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_UPDATE.format('factura del cliente')
    template_name = 'core/facturacliente_form.html'

    def get_form_kwargs(self):
        """Envía parámetros extras al formulario."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('core:factura-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina una factura."""

    model = Factura
    permission_required = 'core.delete_factura'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_DELETE.format('factura del cliente')
    success_url = reverse_lazy('core:factura-list')
    template_name = 'core/facturacliente_confirm_delete.html'

    def get_context_data(self, **kwargs):
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        deletable_objects, model_count, protected = get_deleted_objects([self.object])
        context['deletable_objects'] = deletable_objects
        context['model_count'] = dict(model_count).items()
        context['protected'] = protected
        return context

    def delete(self, request, *args, **kwargs):
        """Sobreescribe método para eliminar una factura.

        Si elimino una factura y está asociada a una cobranza que la tiene por única
        factura, elimino la cobranza.
        """
        self.object = self.get_object()

        cobranza_factura = CobranzaFactura.objects.filter(factura=self.object).first()
        if cobranza_factura:
            count = cobranza_factura.cobranza.cobranza_facturas.count()
            if count == 1:
                Cobranza.objects.get(pk=cobranza_factura.cobranza.pk).delete()

        # Elimino los archivos asociados
        self.object.archivos.all().delete()
        self.object.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(self.success_url)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaImportTemplateView(PermissionRequiredMixin, TemplateView):
    """Template para importar facturas."""

    model = Factura
    permission_required = 'core.add_factura'
    raise_exception = True
    template_name = 'core/facturacliente_import.html'

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
