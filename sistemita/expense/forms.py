"""Formulario de fondo y costos."""

# Django
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout, Reset, Submit
from django import forms

# Models
from sistemita.expense.models import Costo


class CostoForm(forms.ModelForm):
    """Formulario del modelo Costo."""

    def __init__(self, *args, **kwargs):
        """Inicialización del formulario."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(Div('fecha', css_class='col-4'), css_class='row'),
                Div(Div('descripcion', css_class='col-6'), css_class='row'),
                Div(Div('fondo', css_class='col-8'), css_class='row'),
                Div(Div('moneda', css_class='col-2'), Div('monto', css_class='col-2'), css_class='row'),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'), Reset('reset', 'Limpiar', css_class='float-right')
            ),
        )

    class Meta:
        """Configuraciones del formulario."""

        model = Costo
        fields = (
            'fecha',
            'descripcion',
            'fondo',
            'moneda',
            'monto',
        )
