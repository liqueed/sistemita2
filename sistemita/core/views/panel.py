"""Vista del panel de control."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

# Sistemita
from sistemita.core.views.home import error_403
from sistemita.utils.strings import MESSAGE_403


class PanelDeControlTemplateView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    """Vista que devuelve un template con la página principal del sitio."""

    permission_required = 'core.view_paneldecontrol'
    raise_exception = True
    template_name = 'core/panel_de_control.html'

    def handle_no_permission(self):
        """Redirige a la página de error 403 si no tiene los permisos y está autenticado."""
        if self.raise_exception and self.request.user.is_authenticated:
            return error_403(self.request, MESSAGE_403)
        return redirect('login')
