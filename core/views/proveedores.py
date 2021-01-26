"""Vistas del modelo Proveedor."""

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
# Django REST Framework
from rest_framework import mixins, permissions, viewsets

from core.forms.proveedores import ProveedorForm
# Models
from core.models.proveedor import Proveedor
from core.serializers import ProveedorSerializer
from core.utils.strings import MESSAGE_403, MESSAGE_SUCCESS_CREATED, MESSAGE_SUCCESS_DELETE, MESSAGE_SUCCESS_UPDATE
from core.views.home import error_403


class ProveedorViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Proveedor view set."""

    queryset = Proveedor.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProveedorSerializer


class ProveedorListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que devuelve un listado de proveedores."""

    paginate_by = 10
    permission_required = 'core.list_proveedor'
    raise_exception = True

    def get_context_data(self, **kwargs):
        """Obtiene datos para incluir en los reportes."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        current_week = date.today().isocalendar()[1]

        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = Proveedor.objects.order_by('id')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(razon_social__search=search) | Q(correo__icontains=search) | Q(cuit__icontains=search)
            )
        return queryset

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class ProveedorCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que agrega un proveedor."""

    form_class = ProveedorForm
    model = Proveedor
    permission_required = 'core.add_proveedor'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_CREATED.format('proveedor')

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('core.change_proveedor'):
            return reverse('core:proveedor-update', args=(self.object.id,))
        if self.request.user.has_perm('core.view_proveedor'):
            return reverse('core:proveedor-detail', args=(self.object.id,))
        if self.request.user.has_perm('core.list_proveedor'):
            return reverse('core:proveedor-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class ProveedorDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de un proveedor."""

    model = Proveedor
    permission_required = 'core.view_proveedor'
    raise_exception = True

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class ProveedorUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un proveedor."""

    form_class = ProveedorForm
    model = Proveedor
    permission_required = 'core.change_proveedor'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_UPDATE.format('proveedor')

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('core:proveedor-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class ProveedorDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina a un proveedor."""

    model = Proveedor
    permission_required = 'core.delete_proveedor'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('proveedor')
    success_url = reverse_lazy('core:proveedor-list')

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
