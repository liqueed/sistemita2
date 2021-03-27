"""Formularios del modelo Group."""

# Django
from django import forms
from django.contrib.auth.models import Group

# Forms
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, Layout, Div, Reset

# Models
from authorization.models import Permission

# Core
from core.utils.strings import HELP_TEXT_MULTIPLE_CHOICE


class GroupForm(forms.ModelForm):
    """Formulario de group."""

    def __init__(self, *args, **kwargs):
        """Inicializacion del Formulario."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['permissions'].widget.attrs['size'] = 10
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('name', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('permissions', css_class='col-6', size=20),
                    css_class='row'
                ),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'),
                Reset('reset', 'Limpiar', css_class='float-right')
            )
        )

    permissions = forms.ModelMultipleChoiceField(
        help_text=HELP_TEXT_MULTIPLE_CHOICE,
        queryset=Permission.objects.filter(
            content_type__app_label__in=['accounting', 'auth', 'authorization', 'core'],
            content_type__model__in=[
                'archivo',
                'cliente', 'factura', 'ordencompra', 'cobranza',
                'proveedor', 'facturaproveedor', 'pago',
                'mediopago',
                'permission', 'user', 'group'
            ]
        ).order_by('content_type__model', 'name')
    )

    class Meta:
        """Configuraciones de formulario."""

        model = Group
        fields = ('name', 'permissions')
