"""Vistas del modelo FacturaDistribuida de clientes."""

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import DeleteView
from django_filters.views import FilterView

# Sistemita
from sistemita.core.models.cliente import FacturaDistribuida
from sistemita.core.views.home import error_403
from sistemita.utils.commons import get_deleted_objects
from sistemita.utils.strings import _MESSAGE_SUCCESS_DELETE, MESSAGE_403


class FacturaDistribuidaListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que muestra un listado de facturas imputadas."""

    model = FacturaDistribuida
    paginate_by = 10
    permission_required = 'core.list_facturadistribuida'
    raise_exception = True
    template_name = 'core/facturadistribuida_list.html'

    def get_queryset(self):
        """
        Sobreescribe queryset.
        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = FacturaDistribuida.objects.order_by('-factura__creado')
        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', None)
        try:
            if search:
                search = search.strip()
                queryset = queryset.filter(
                    Q(factura__numero__icontains=search)
                    | Q(factura__cliente__razon_social__icontains=search)
                    | Q(factura__cliente__cuit__icontains=search)
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
        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaDistribuidaCreateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista para decidir la distribución de una factura de cliente."""

    permission_required = 'core.add_facturadistribuida'
    raise_exception = True
    template_name = 'core/facturadistribuida_create.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaDistribuidaUpdateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista para editar la distribución de una factura de cliente."""

    permission_required = 'core.change_facturadistribuida'
    raise_exception = True
    template_name = 'core/facturadistribuida_update.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaDistribuidaDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de una factura distribuida."""

    model = FacturaDistribuida
    permission_required = 'core.view_facturadistribuida'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaDistribuidaDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina o resetea la distribución de una factura."""

    model = FacturaDistribuida
    permission_required = 'core.delete_facturadistribuida'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_DELETE.format('factura imputada')
    success_url = reverse_lazy('core:facturadistribuida-list')
    template_name = 'core/facturadistribuida_confirm_delete.html'

    def get_context_data(self, **kwargs):
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        deletable_objects, model_count, protected = get_deleted_objects([self.object])
        context['deletable_objects'] = deletable_objects
        context['model_count'] = dict(model_count).items()
        context['protected'] = protected
        return context

    def delete(self, request, *args, **kwargs):
        """
        Al eliminar la distribución la factura, la misma se resetea.
        """
        self.object = self.get_object()
        self.object.distribuida = False
        self.object.monto_distribuido = 0
        self.object.save()
        self.object.factura_distribuida_proveedores.all().delete()

        success_url = self.get_success_url()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(success_url)
