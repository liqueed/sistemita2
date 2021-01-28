"""Vistas del modelo de Pago."""

# Imports
import tempfile

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F, Q, Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, TemplateView

# Django Rest Framework
from rest_framework import mixins, permissions, viewsets

# Accounting
from accounting.models.pago import Pago
from accounting.serializers.pagos import PagoSerializer

# Core
from core.models.proveedor import FacturaProveedor
from core.utils.strings import MESSAGE_403, MESSAGE_SUCCESS_DELETE
from core.views.home import error_403

# Utils
from weasyprint import HTML


class PagoViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """Pago view set."""

    queryset = Pago.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PagoSerializer


class PagoListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que devuelve un listado de pagos."""

    paginate_by = 10
    permission_required = 'accounting.list_pago'
    raise_exception = True

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        current_week = date.today().isocalendar()[1]

        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context

    def get_queryset(self):
        """Modifica el orden y devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Pago.objects.order_by('-fecha')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(proveedor__razon_social__icontains=search) | Q(proveedor__correo__icontains=search) |
                Q(proveedor__cuit__icontains=search)
            )

        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class PagoCreateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista que muestra un formulario para agregar un pago."""

    permission_required = 'accounting.add_pago'
    raise_exception = True
    template_name = 'accounting/pago_create.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class PagoDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra los detalles de un pago."""

    model = Pago
    permission_required = 'accounting.view_pago'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class PagoUpdateTemplateView(PermissionRequiredMixin, TemplateView):
    """Vista para editar una cobranza."""

    permission_required = 'accounting.change_pago'
    raise_exception = True
    template_name = 'accounting/pago_update.html'

    def get_context_data(self, **kwargs):
        """Envía al template la clave primaria."""
        context = super().get_context_data(**kwargs)
        context['pk'] = kwargs['pk']
        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class PagoDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar un pago."""

    model = Pago
    permission_required = 'accounting.delete_pago'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('pago')
    success_url = reverse_lazy('accounting:pago-list')

    def delete(self, request, *args, **kwargs):
        """Modifica el estado de las facturas que son desasociadas del pago al eliminarse."""
        pago = self.get_object()

        pago_facturas = pago.pago_facturas.all()
        for c_factura in pago_facturas:
            FacturaProveedor.objects.filter(pk=c_factura.factura.id).update(
                cobrado=False
            )

        success_url = self.get_success_url()
        pago.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(success_url)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class PagoGeratePDFDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra los detalles de un pago."""

    model = Pago
    permission_required = 'accounting.view_pago'
    raise_exception = True
    template_name = 'accounting/pago_pdf.html'

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        # TODO: Quitar, solo de prueba
        context = super().get_context_data(**kwargs)
        pago = context['object']
        context['subtotal_comprobantes'] = self.get_queryset().filter(pk=pago.pk).aggregate(Sum('total'))
        context['subtotal_retenciones'] = self.get_queryset().filter(pk=pago.pk).annotate(
            sub=Sum(F('pago_facturas__ganancias') + F('pago_facturas__iva') + F('pago_facturas__ingresos_brutos')))

        return context

    def get(self, request, *args, **kwargs):
        """Devuelve un comprobante de pago en formato PDF."""
        pago = self.get_object()
        queryset = self.get_queryset()

        subtotal_comprobantes = self.get_queryset().filter(pk=pago.pk).aggregate(Sum('total'))
        subtotal_retenciones = queryset.filter(pk=pago.pk).annotate(
            sub=Sum(F('pago_facturas__ganancias') + F('pago_facturas__iva') + F('pago_facturas__ingresos_brutos'))
        )

        # Rendered
        html_string = render_to_string('accounting/pago_pdf.html', {
            'object': pago,
            'subtotal_comprobantes': subtotal_comprobantes,
            'subtotal_retenciones': subtotal_retenciones
        })
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        result = html.write_pdf(presentational_hints=True)

        # Creating http response
        response = HttpResponse(content_type='application/pdf;')
        response['Content-Disposition'] = 'inline; filename=comprobante_de_pago.pdf'
        response['Content-Transfer-Encoding'] = 'binary'
        with tempfile.NamedTemporaryFile(delete=True) as output:
            output.write(result)
            output.flush()
            output = open(output.name, 'rb')
            response.write(output.read())

        return response

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
