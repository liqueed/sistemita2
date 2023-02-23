"""Formularios del modelo Group."""

# Forms
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout, Reset, Submit

# Django
from django import forms
from django.contrib.auth.models import Group

# Sistemita
from sistemita.authorization.models import Permission
from sistemita.utils.strings import HELP_TEXT_MULTIPLE_CHOICE


class GroupForm(forms.ModelForm):
    """Formulario de group."""

    def __init__(self, *args, **kwargs):
        """Inicializacion del Formulario."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['autocomplete'] = 'off'
        self.helper = FormHelper()
        self.fields['permissions'].widget.attrs['size'] = 10
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(Div('name', css_class='col-6'), css_class='row'),
                Div(Div('permissions', css_class='col-6', size=20), css_class='row'),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'), Reset('reset', 'Limpiar', css_class='float-right')
            ),
        )

    permissions = forms.ModelMultipleChoiceField(
        help_text=HELP_TEXT_MULTIPLE_CHOICE,
        queryset=Permission.objects.filter(
            content_type__app_label__in=['accounting', 'auth', 'authorization', 'core', 'expense'],
            content_type__model__in=[
                'archivo',
                'cliente',
                'factura',
                'contrato',
                'cobranza',
                'proveedor',
                'facturadistribuida',
                'facturaproveedor',
                'pago',
                'mediopago',
                'permission',
                'user',
                'group',
                'fondo',
                'costo',
            ],
        ).order_by('content_type__model', 'name'),
    )

    class Meta:
        """Configuraciones de formulario."""

        model = Group
        fields = ('name', 'permissions')
