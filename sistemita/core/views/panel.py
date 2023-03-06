"""Vista del panel de control."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import TemplateView


class PanelDeControlTemplateView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    """Vista que devuelve un template con la página principal del sitio."""

    template_name = 'core/panel_de_control.html'
