"""Formulario del modelo Permission."""

# Django
from django import forms

# Forms
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, Layout, Div, Reset

# Models
from authorization.models import ContentType, Permission


class PermissionForm(forms.ModelForm):
    """Formulario de permisos."""

    def __init__(self, *args, **kwargs):
        """Inicializacion del Formulario."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('name', css_class='col-4'),
                    css_class='row'
                ),
                Div(
                    Div('content_type', css_class='col-4'),
                    css_class='row'
                ),
                Div(
                    Div('codename', css_class='col-4'),
                    css_class='row'
                ),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'),
                Reset('reset', 'Limpiar', css_class='float-right')
            )
        )

    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            app_label__in=['accounting', 'auth', 'authorization', 'core'],
            model__in=[
                 'archivo',
                 'cliente', 'factura', 'ordencompra', 'cobranza',
                 'proveedor', 'facturaproveedor', 'pago',
                 'mediopago',
                 'permission', 'user', 'group'
            ]
        ).order_by('model'), label='Modulo'
    )

    class Meta:
        """Configuraciones de formulario."""

        model = Permission
        fields = ('name', 'content_type', 'codename')
