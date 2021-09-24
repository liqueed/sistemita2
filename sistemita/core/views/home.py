"""Vistas de la sección principal."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    """Vista que devuelve un template con la página principal del sitio."""

    template_name = 'core/home.html'


def error_403(request, exception):
    """Devuelve template de acceso denegado."""
    return render(request, '403.html', context={'exception': exception}, status=403)


def error_404(request, exception):
    """Return template 404."""
    print('here')
    return render(request, '404.html', context={'exception': exception}, status=404)


def error_500(request):
    """Return template 500."""
    return render(request, '500.html')
