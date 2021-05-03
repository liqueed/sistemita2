"""Formulario de medio de pago."""

# Crispy
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout, Reset, Submit

# Django
from django import forms

# Models
from sistemita.core.models.mediopago import MedioPago


class MedioPagoForm(forms.ModelForm):
    """Formulario de medio de pago."""

    def __init__(self, *args, **kwargs):
        """Inicialización del formulario."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['autocomplete'] = 'off'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(
                    Div('nombre', css_class='col-4'),
                    css_class='row'
                ),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'),
                Reset('reset', 'Limpiar', css_class='float-right')
            )
        )

    class Meta:
        """Configuraciones del formulario."""

        model = MedioPago
        fields = ('nombre', )
