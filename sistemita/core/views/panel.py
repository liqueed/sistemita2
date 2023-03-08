"""Vista del panel de control."""

# Django
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

# Sistemita
from sistemita.core.models.cliente import Contrato, Factura
from sistemita.core.models.proveedor import Proveedor
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

    def render_to_response(self, context, **response_kwargs):
        """
        Return a response, using the `response_class` for this view, with a
        template rendered with the given context.
        Pass response_kwargs to the constructor of the response class.
        """
        user_email = self.request.user.email
        proveedor = Proveedor.objects.filter(correo=user_email).first()
        context['contratos'] = Contrato.objects.filter(proveedores__in=[proveedor.pk], factura__isnull=True)
        context['facturas'] = Factura.objects.filter(proveedores__in=[proveedor.pk])
        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )
