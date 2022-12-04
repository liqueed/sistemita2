"""Vistas del modelo FacturaDistribuida de clientes."""

# Datetime
from datetime import date

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Q
from django.shortcuts import redirect
from django_filters.views import FilterView

# Sistemita
from sistemita.core.models.cliente import FacturaDistribuida
from sistemita.core.views.home import error_403
from sistemita.utils.strings import MESSAGE_403


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
        queryset = FacturaDistribuida.objects.order_by('-creado')
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
        context['last_created'] = queryset.filter(creado__week=current_week).count()

        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
