from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.postgres.search import SearchVector
from django.views.generic import TemplateView, ListView

from authorization.models import User
from core.models import Cliente


class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    queryset = Cliente.objects.all()


class UsuarioListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'core/user_list.html'
    queryset = User.objects.order_by('username')

    def get_queryset(self):
        # Search filter
        search = self.request.GET.get('search', None)
        if search:
            # self.queryset = self.queryset.annotate(
            #     search=SearchVector('last_name') + SearchVector('first_name') + SearchVector('email') + SearchVector('username'),
            # ).filter(search=search)
            self.queryset = self.queryset.filter(username__search=search)

        return self.queryset


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'
