"""Vistas del modelo Factura.

El modelo Factura está asociado al modelo cliente.
"""
# Datetime
from datetime import datetime, timedelta

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
# Django REST Framework
from rest_framework import mixins, permissions, viewsets

# Accounting
from accounting.models.cobranza import Cobranza, CobranzaFactura
# Core
from core.filters import FacturaFilterSet
from core.forms.clientes import FacturaForm
from core.models.cliente import Factura
from core.serializers import FacturaSerializer
from core.utils.strings import (_MESSAGE_SUCCESS_CREATED,
                                _MESSAGE_SUCCESS_DELETE,
                                _MESSAGE_SUCCESS_UPDATE, MESSAGE_403)
from core.views.home import error_403


class FacturaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Factura view set."""

    filter_fields = ('cliente', 'cobrado')
    queryset = Factura.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FacturaSerializer


class FacturaListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que muestra un listado de facturas."""

    filterset_class = FacturaFilterSet
    paginate_by = 10
    permission_required = 'core.list_factura'
    raise_exception = True
    template_name = 'core/facturacliente_list.html'

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        context['due'] = queryset.filter(cobrado=False).aggregate(
            Sum('total'), Count('id')
        )
        context['last_created'] = queryset.filter(
            creado__gte=datetime.now()-timedelta(days=7)
        ).count()

        return context

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza una búsqueda.
        """
        queryset = Factura.objects.order_by('-fecha')
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(cliente__razon_social__icontains=search) |
                Q(cliente__correo__icontains=search) |
                Q(cliente__cuit__icontains=search)
            )

        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class FacturaCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista para agregar una factura."""

    model = Factura
    form_class = FacturaForm
    permission_required = 'core.add_factura'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_CREATED.format('factura del cliente')
    template_name = 'core/facturacliente_form.html'

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

    def delete(self, request, *args, **kwargs):
        """Sobreescribe método para eliminar una factura.

        Si elimino una factura y está asociada a una cobranza que la tiene por única
        factura, elimino la cobranza.
        """
        factura = self.get_object()

        cobranza_factura = CobranzaFactura.objects.filter(factura=factura).first()
        if cobranza_factura:
            count = cobranza_factura.cobranza.cobranza_facturas.count()
            if count == 1:
                Cobranza.objects.get(pk=cobranza_factura.cobranza.pk).delete()

        # Elimino los archivos asociados
        factura.archivos.all().delete()
        factura.delete()
        messages.success(request, self.success_message)
        return HttpResponseRedirect(self.success_url)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
