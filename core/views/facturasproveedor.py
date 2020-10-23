from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django_filters.views import FilterView


from core.models import FacturaProveedor
from core.filters import FacturaProveedorFilterSet


class FacturaProveedorListView(LoginRequiredMixin, FilterView):
    filterset_class = FacturaProveedorFilterSet

    def get_queryset(self):
        queryset = FacturaProveedor.objects.all()
        search = self.request.GET.get('search', None)
        if search:
            self.queryset = queryset.filter(
                Q(proveedor__razon_social__icontains=search) |
                Q(proveedor__correo__icontains=search) |
                Q(proveedor__cuit__icontains=search)
            )

        return self.queryset
