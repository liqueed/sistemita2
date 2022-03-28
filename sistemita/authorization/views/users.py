"""Vistas del módulo de usuarios."""

# Datetime
from datetime import date

# Django
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldError
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, ListView
from django.views.generic.edit import CreateView, UpdateView

# Sistemita
from sistemita.authorization.forms.users import (
    PasswordResetForm,
    UserCreateForm,
    UserUpdateForm,
)
from sistemita.core.views.home import error_403
from sistemita.utils.commons import get_deleted_objects
from sistemita.utils.strings import (
    _MESSAGE_SUCCESS_UPDATE,
    MESSAGE_403,
    MESSAGE_SUCCESS_CREATED,
    MESSAGE_SUCCESS_DELETE,
    MESSAGE_SUCCESS_UPDATE,
)

User = get_user_model()


class UserListView(PermissionRequiredMixin, SuccessMessageMixin, ListView):
    """Vista que retorna un listado de usuarios."""

    paginate_by = 10
    permission_required = 'authorization.list_user'
    raise_exception = True
    template_name = 'authorization/user_list.html'

    def get_queryset(self):
        """Devuelve los resultados de la búsqueda realizada por el usuario."""
        queryset = User.objects.order_by('username')

        search = self.request.GET.get('search', None)
        order_by = self.request.GET.get('order_by', None)
        try:
            if search:
                queryset = queryset.filter(
                    Q(username__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search)
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

        context['last_created'] = queryset.filter(date_joined__week=current_week).count()

        return context

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class UserCreateFormView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista que crea un usuario."""

    model = User
    form_class = UserCreateForm
    permission_required = 'authorization.add_user'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_CREATED.format('usuario')
    template_name = 'authorization/user_form.html'

    def get_success_url(self):
        """Luego de agregar al objecto redirecciono a la vista que tiene permiso."""
        if self.request.user.has_perm('authorization.change_user'):
            return reverse('authorization:user-update', args=(self.object.id,))
        if self.request.user.has_perm('authorization.view_user'):
            return reverse('authorization:user-detail', args=(self.object.id,))
        if self.request.user.has_perm('authorization.list_user'):
            return reverse('authorization:user-list')
        return reverse('core:home')

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class UserDetailView(PermissionRequiredMixin, SuccessMessageMixin, DetailView):
    """Vista que muestra el detalle de un usuario."""

    model = User
    permission_required = 'authorization.view_user'
    raise_exception = True
    template_name = 'authorization/user_detail.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class UserUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista que modifica un usuario."""

    form_class = UserUpdateForm
    model = User
    permission_required = 'authorization.change_user'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_UPDATE.format('usuario')
    template_name = 'authorization/user_form.html'

    def get_success_url(self):
        """Luego de editar al objecto muestra la misma vista."""
        return reverse('authorization:user-update', args=(self.object.id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class UserDeleteView(PermissionRequiredMixin, DeleteView):
    """Vista que elimina un usuario."""

    model = User
    permission_required = 'authorization.delete_user'
    raise_exception = True
    success_message = MESSAGE_SUCCESS_DELETE.format('usuario')
    success_url = reverse_lazy('authorization:user-list')
    template_name = 'authorization/user_confirm_delete.html'

    def get_context_data(self, **kwargs):
        """Agrega datos al contexto."""
        context = super().get_context_data(**kwargs)
        deletable_objects, model_count, protected = get_deleted_objects([self.object])
        context['deletable_objects'] = deletable_objects
        context['model_count'] = dict(model_count).items()
        context['protected'] = protected
        return context

    def delete(self, request, *args, **kwargs):
        """Muestra un mensaje sobre el resultado de la acción."""
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')


class PasswordChangeFormView(PermissionRequiredMixin, SuccessMessageMixin, FormView):
    """Vista que cambia la contraseña de un usuario."""

    form_class = PasswordResetForm
    permission_required = 'authorization.change_user'
    raise_exception = True
    success_message = _MESSAGE_SUCCESS_UPDATE.format('contraseña')
    template_name = 'authorization/password_change.html'

    def get_form_kwargs(self):
        """Envia a la instancia del formulario al usuario a modificar."""
        kwargs = super().get_form_kwargs()
        object_id = self.kwargs['pk']
        user = User.objects.get(pk=object_id)
        kwargs['user'] = user
        return kwargs

    def get_context_data(self, **kwargs):
        """Envía al contexto el username del usuario."""
        context = super().get_context_data(**kwargs)
        username = context['form'].user.username
        context['username'] = username
        return context

    def form_valid(self, form):
        """Guarda el formulario validado."""
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Luego de editar al objecto regreso al formulario principal."""
        object_id = self.kwargs['pk']
        return reverse('authorization:user-update', args=(object_id,))

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
