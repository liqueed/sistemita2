"""Vistas del módulo de usuarios."""

# Django
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Forms
from authorization.forms import UserForm

# Models
from django.contrib.auth import get_user_model

# Utils
from core.utils.strings import (
    MESSAGE_SUCCESS_CREATED, MESSAGE_SUCCESS_UPDATE, MESSAGE_SUCCESS_DELETE
)

User = get_user_model()


class UserListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que retorna un listado de usuarios."""

    paginate_by = 10
    permission_required = 'authorization.list_user'
    template_name = 'authorization/user_list.html'

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


class UserCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que crea un usuario."""

    form_class = UserForm
    model = User
    permission_required = 'authorization.add_user'
    success_message = MESSAGE_SUCCESS_CREATED.format('usuario')
    template_name = 'authorization/user_form.html'

    def get_success_url(self):
        """Luego de agregar al objecto muestra la misma vista."""
        return reverse('authorization:user-update', args=(self.object.id,))


class UserDetailView(PermissionRequiredMixin, DetailView):
    """Vista que muestra el detalle de un usuario."""

    model = User
    permission_required = 'authorization.view_user'
    template_name = 'authorization/user_detail.html'


class UserUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un usuario."""

    form_class = UserForm
    model = User
    permission_required = 'authorization.change_user'
    success_message = MESSAGE_SUCCESS_UPDATE.format('usuario')
    template_name = 'authorization/user_form.html'

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('authorization:user-update', args=(self.object.id,))


class UserDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina un usuario."""

    model = User
    permission_required = 'authorization.delete_user'
    success_message = MESSAGE_SUCCESS_DELETE.format('usuario')
    success_url = reverse_lazy('authorization:user-list')
    template_name = 'authorization/user_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super(UserDeleteView, self).delete(request, *args, **kwargs)
