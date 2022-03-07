"""Formulario de fondo y costos."""

# Django
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout, Reset, Submit
from django import forms
from django.db.models import Sum

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
                Div(Div('descripcion', css_class='col-10'), css_class='row'),
                Div(Div('fondo', css_class='col-10'), css_class='row'),
                Div(Div('moneda', css_class='col-2'), Div('monto', css_class='col-2'), css_class='row'),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'), Reset('reset', 'Limpiar', css_class='float-right')
            ),
        )

    monto = forms.DecimalField(required=True, min_value=1, decimal_places=2, max_digits=12, initial=0.0)

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
        fondo = data.get('fondo', None)

        if not fondo:
            raise forms.ValidationError({'fondo': 'Campo requerido.'})

        if data.get('moneda') != data.get('fondo').factura.moneda:
            raise forms.ValidationError({'moneda': 'La moneda debe ser igual a la moneda de la factura.'})

        if not self.instance.pk:
            if monto > fondo.monto_disponible:
                raise forms.ValidationError({'monto': 'El monto debe ser menor o igual al monto disponible.'})
        else:
            # Al editar valida que no supere el monto original sumando a otros costos para el mismo fondo
            other_costos = Costo.objects.filter(fondo=self.instance.fondo).exclude(pk=self.instance.pk)
            if other_costos.exists():
                sum_costos = other_costos.aggregate(otros_costos=Sum('monto')).get('otros_costos')
                # el monto ingresado es mayor
                if monto > self.instance.monto:
                    if float(sum_costos + monto) > self.instance.fondo.monto:
                        raise forms.ValidationError(
                            {'monto': 'La suma de costos para este fondo supera el monto del fondo.'}
                        )

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
            if instance.monto != monto:
                diff = abs(instance.monto - monto)
                if monto > instance.monto:
                    # el monto ingresado es mayor
                    instance.fondo.monto_disponible -= diff
                else:
                    instance.fondo.monto_disponible += diff
            costo_qs.update(**data)

        # Disponibilidad
        instance.fondo.disponible = bool(instance.fondo.monto_disponible)
        instance.fondo.save()
        instance.refresh_from_db()

        return instance
