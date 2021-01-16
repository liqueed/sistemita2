"""Vistas del modelo FacturaProveedor."""

# Datetime
from datetime import date

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

# Core
from core.filters import FacturaProveedorFilterSet
from core.forms.proveedores import FacturaProveedorForm
from core.models.proveedor import FacturaProveedor
from core.serializers import FacturaProveedorSerializer
from core.utils.strings import _MESSAGE_SUCCESS_CREATED, _MESSAGE_SUCCESS_DELETE, _MESSAGE_SUCCESS_UPDATE, MESSAGE_403
from core.views.home import error_403


class FacturaProveedorViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Factura de proveedores view set."""

    filter_fields = ('proveedor', 'cobrado')
    queryset = FacturaProveedor.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = FacturaProveedorSerializer


class FacturaProveedorListView(PermissionRequiredMixin, SuccessMessageMixin, FilterView):
    """Vista que retorna un lista de facturas a proveedores."""

    filterset_class = FacturaProveedorFilterSet
    paginate_by = 10
    permission_required = 'core.list_facturaproveedor'
    raise_exception = True
    template_name = 'core/facturaproveedor_list.html'

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        current_week = date.today().isocalendar()[1]

        context['due'] = queryset.filter(cobrado=False).aggregate(
            Sum('total'), Count('id')
        )
        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = FacturaProveedor.objects.order_by('-fecha')

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


class FacturaProveedorCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que create un factura a proveedor."""

    form_class = FacturaProveedorForm
    model = FacturaProveedor
    permission_required = 'core.add_facturaproveedor'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_CREATED.format('factura a proveedor')

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
        return redirect('login')
