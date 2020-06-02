from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, ListView

from authorization.models import User
from core.models import Cliente


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    queryset = Cliente.objects.all()


class UsuarioListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'core/user_list.html'
    queryset = User.objects.all().order_by('username')


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'
