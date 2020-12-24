"""Vistas de la sección principal."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):
    """Vista que devuelve un template con la página principal del sitio."""

    template_name = 'core/home.html'


def error_403(request, exception):
    """Devuelve template de acceso denegado."""
    return render(request, '403.html')
