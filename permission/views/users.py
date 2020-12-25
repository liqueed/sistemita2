"""Vistas del módulo de usuarios."""

# Django
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Forms
from permission.forms import UserForm

# Models
from authorization.models import User


class UserListView(PermissionRequiredMixin, ListView):
    """Vista que retorna un listado de usuarios."""

    paginate_by = 10
    permission_required = 'authorization.list_user'
    template_name = 'permission/user_list.html'

    def get_queryset(self):
        """Sobreescribe queryset.

        Devuelve un conjunto de resultados si el usuario realiza un búsqueda.
        """
        queryset = User.objects.order_by('username')

        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__search=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        return queryset


class UserCreateView(PermissionRequiredMixin, CreateView):
    """Vista que crea un usuario."""

    form_class = UserForm
    model = User
    permission_required = 'authorization.add_user'
    success_url = reverse_lazy('permission:user-list')
    template_name = 'permission/user_form.html'


class UserDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra el detalle de un usuario."""

    model = User
    permission_required = 'authorization.view_user'
    template_name = 'permission/user_detail.html'


class UserUpdateView(PermissionRequiredMixin, UpdateView):
    """Vista que modifica un usuario."""

    form_class = UserForm
    model = User
    permission_required = 'authorization.change_user'
    success_url = reverse_lazy('permission:user-list')
    template_name = 'permission/user_form.html'


class UserDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina un usuario."""

    model = User
    permission_required = 'authorization.delete_user'
    success_url = reverse_lazy('permission:user-list')
    template_name = 'permission/user_confirm_delete.html'
