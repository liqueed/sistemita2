"""Vistas de grupos."""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView, DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

# Models
from django.contrib.auth.models import Group

# Forms
from permission.forms import GroupForm


class GroupListView(PermissionRequiredMixin, ListView):
    """Listado de Grupos."""

    permission_required = 'auth.list_group'
    paginate_by = 10
    template_name = 'permission/group_list.html'

    def get_queryset(self):
        """Devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Group.objects.all()

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset


class GroupCreateView(PermissionRequiredMixin, CreateView):
    """Vista para crear un grupo."""

    model = Group
    form_class = GroupForm
    permission_required = 'auth.add_group'
    template_name = 'permission/group_form.html'
    success_url = reverse_lazy('permission:group-list')


class GroupDetailtView(PermissionRequiredMixin, DetailView):
    """Vista para ver el detalle de un grupo."""

    model = Group
    permission_required = 'auth.view_group'
    template_name = 'permission/group_detail.html'


class GroupUpdateView(PermissionRequiredMixin, UpdateView):
    """Vista para editar un grupo."""

    model = Group
    form_class = GroupForm
    permission_required = 'auth.change_group'
    template_name = 'permission/group_form.html'
    success_url = reverse_lazy('permission:group-list')


class GroupDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista para eliminar un grupo."""

    model = Group
    permission_required = 'auth.delete_group'
    template_name = 'permission/group_confirm_delete.html'
    success_url = reverse_lazy('permission:group-list')
