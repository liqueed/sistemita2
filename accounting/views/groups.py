"""Vistas de grupos."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy

# Models
from django.contrib.auth.models import Group

# Forms
from accounting.forms import GroupForm


class GroupListView(LoginRequiredMixin, ListView):
    """Listado de Grupos."""

    template_name = 'accounting/group_list.html'

    def get_queryset(self):
        """Devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = Group.objects.all()

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset


class GroupCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear un grupo."""

    model = Group
    form_class = GroupForm
    template_name = 'accounting/group_form.html'
    success_url = reverse_lazy('accounting:group-list')


class GroupDetailtView(LoginRequiredMixin, DetailView):
    """Vista para ver el detalle de un grupo."""

    model = Group
    template_name = 'accounting/group_detail.html'


class GroupUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar un grupo."""

    model = Group
    form_class = GroupForm
    template_name = 'accounting/group_form.html'
    success_url = reverse_lazy('accounting:group-list')


class GroupDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar un grupo."""

    model = Group
    template_name = 'accounting/group_confirm_delete.html'
    success_url = reverse_lazy('accounting:group-list')
