"""Formulario de fondo y costos."""

# Django
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout, Reset, Submit
from django import forms

# Models
from sistemita.expense.models import Costo, Fondo


class CostoForm(forms.ModelForm):
    """Formulario del modelo Costo."""

    def __init__(self, *args, **kwargs):
        """Inicialización del formulario."""
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if not instance:
            self.fields['fondo'].queryset = Fondo.objects.filter(
                disponible=True,
                monto_disponible__gt=0
            ).order_by('-factura__fecha')

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

    def clean(self):
        """Valida que el monto sea menor o igual al monto disponible del fondo."""
        data = super().clean()
        monto = data.get('monto')
        fondo = data.get('fondo')

        if data.get('moneda') != data.get('fondo').factura.moneda:
            raise forms.ValidationError({'moneda': 'La moneda debe ser igual a la moneda de la factura.'})

        if not self.instance.pk:
            if monto > fondo.monto_disponible:
                raise forms.ValidationError({'monto': 'El monto debe ser menor o igual al monto disponible.'})
        else:
            if monto > fondo.monto:
                raise forms.ValidationError({'monto': 'El monto debe ser menor o igual al monto.'})

        return data

    def save(self, commit=True):
        """Guarda los datos recibidos del formulario."""
        data = self.cleaned_data
        instance = self.instance
        monto = data.get('monto')
        fondo_input = data.get('fondo')

        if not self.has_changed():
            return instance

        if instance.pk is None:
            instance = Costo.objects.create(**data)
            instance.fondo.monto_disponible -= monto
        else:
            costo_qs = Costo.objects.filter(pk=instance.pk)
            instance = costo_qs.first()

            # Caso: costo cambie de fondo, actualizo el fondo anterior
            if fondo_input.pk != instance.fondo.pk:
                instance.fondo.disponible = True
                instance.fondo.monto_disponible += monto
                instance.fondo.save()

            # Caso: cambio el monto del costo
            if instance.monto != self.instance.monto:
                if self.instance.monto > instance.monto:
                    # el monto ingresado es mayor
                    diff = self.instance.monto - instance.monto
                    instance.fondo.monto_disponible -= diff
                    instance.fondo.save()
                else:
                    diff = instance.monto - self.instance.monto
                    instance.fondo.monto_disponible += diff
                    instance.fondo.save()

            costo_qs.update(**data)

        # Disponibilidad
        if instance.fondo.monto_disponible == 0:
            instance.fondo.disponible = False
        else:
            instance.fondo.disponible = True

        instance.fondo.save()
        instance.refresh_from_db()

        return instance
