"""Vista del panel de control."""

# Django
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

# Sistemita
from sistemita.core.models.cliente import Contrato, Factura
from sistemita.core.models.proveedor import Proveedor
from sistemita.core.views.home import error_403
from sistemita.utils.commons import get_groups_to_panel
from sistemita.utils.strings import MESSAGE_403


class PanelDeControlTemplateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, TemplateView):
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
        proveedor = Proveedor.objects.filter(correo=user_email).values('id')

        if proveedor:
            proveedor_id = proveedor.first().get('id')
            context['contratos'] = Contrato.objects.filter(proveedores__in=[proveedor_id], monto__gt=0).values(
                'cliente__razon_social', 'detalle', 'moneda', 'monto'
            )

            # Define cards para el panel
            facturas = sorted(Factura.objects.filter(proveedores__in=[proveedor_id]), key=lambda f: f.status)

            groups = []
            while len(facturas):
                facturas, sub_group = get_groups_to_panel(facturas)
                if sub_group:
                    groups.append(sub_group)

                context['groups'] = groups

        response_kwargs.setdefault('content_type', self.content_type)
        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            using=self.template_engine,
            **response_kwargs
        )
