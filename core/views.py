from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, ListView

from authorization.models import User


class ClienteListView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'


class UsuarioListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'core/user_list.html'


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'
