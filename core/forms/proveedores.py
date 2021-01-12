"""Formularios de proveedor."""

# Django
from django import forms

# Crispy
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, Layout, HTML, Div, Reset

# Models
from core.models.archivo import Archivo
from core.models.entidad import Distrito, Localidad
from core.models.proveedor import FacturaProveedor, Proveedor


class ProveedorForm(forms.ModelForm):
    """Formulario de proveedor."""

    def __init__(self, *args, **kwargs):
        """Inicialización del formulario."""
        super().__init__(*args, **kwargs)

        if 'data' in kwargs.keys():
            if 'provincia' in kwargs['data'].keys():
                provincia = kwargs['data'].get('provincia', None)
                if provincia:
                    self.fields['distrito'].queryset = Distrito.objects.filter(
                        provincia=provincia
                    )

            if 'distrito' in kwargs['data'].keys():
                distrito = kwargs['data'].get('distrito', None)
                if distrito:
                    self.fields['localidad'].queryset = Localidad.objects.filter(
                        distrito=distrito
                    )
        else:
            if self.instance and self.instance.provincia:
                self.fields['distrito'].queryset = Distrito.objects.filter(
                    provincia=self.instance.provincia
                )
            else:
                self.fields['distrito'].queryset = Distrito.objects.none()

            if self.instance and self.instance.distrito:
                self.fields['localidad'].queryset = Localidad.objects.filter(
                    distrito=self.instance.distrito
                )
            else:
                self.fields['localidad'].queryset = Localidad.objects.none()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(
                    Div('razon_social', css_class='col-8'),
                    Div('cuit', css_class='col-4'),
                    css_class='row'
                ),
                Div(
                    Div('correo', css_class='col-6'),
                    Div('telefono', css_class='col-6'),
                    css_class='row'
                ),
                HTML("""<legend>Dirección</legend>"""),
                Div(
                    Div('calle', css_class='col-6'),
                    Div('numero', css_class='col-2'),
                    Div('piso', css_class='col-2'),
                    Div('dpto', css_class='col-2'),
                    css_class='row'
                ),
                Div(
                    Div('provincia', css_class='col-4'),
                    Div('distrito', css_class='col-4'),
                    Div('localidad', css_class='col-4'),
                    css_class='row'
                ),
                HTML("""<legend>Pagos</legend>"""),
                Div(
                    Div('cbu', css_class='col-6'),
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

        model = Proveedor
        fields = (
            'razon_social', 'cuit', 'correo', 'telefono',
            'calle', 'numero', 'piso', 'dpto',
            'provincia', 'distrito', 'localidad',
            'cbu'
        )


class FacturaProveedorForm(forms.ModelForm):
    """Formulario de factura de proveedor."""

    def __init__(self, *args, **kwargs):
        """Inicialización de formulario."""
        super().__init__(*args, **kwargs)
        self.fields['numero'].label = 'Número de factura'
        self.fields['factura'].label = 'Factura de cliente'
        self.fields['cobrado'].label = 'Pagado'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(
                    Div('fecha', css_class='col-4'),
                    css_class='row'
                ),
                Div(
                    Div('numero', css_class='col-4'),
                    Div('tipo', css_class='col-2'),
                    css_class='row'
                ),
                Div(
                    Div('proveedor', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('factura', css_class='col-6'),
                    css_class='row'
                ),
                # Aca va la data extra del cliente por JS
                Div(css_id='info_proveedor', css_class='row'),
                Div(
                    Div('detalle', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('moneda', css_class='col-2'),
                    Div('neto', css_class='col-4'),
                    css_class='row'
                ),
                Div(
                    Div('iva', css_class='col-2'),
                    css_class='row'
                ),
                Div(
                    Div('total', css_class='col-4'),
                    css_class='row'
                ),
                Div(
                    Div('cobrado', css_class='col-2'),
                    css_class='row'
                ),
                Div(
                    Div('archivos', template='components/input_files.html'),
                    css_class='row'
                ),
                Div(css_id='adjuntos', css_class='row'),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'),
                Reset('reset', 'Limpiar', css_class='float-right')
            )
        )

    archivos = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}),
        required=False
    )

    class Meta:
        """Configuraciones de formulario."""

        model = FacturaProveedor
        fields = (
            'fecha', 'numero', 'tipo', 'proveedor', 'factura', 'detalle',
            'moneda', 'neto', 'iva', 'total', 'cobrado', 'archivos'
        )

    def save(self, *args, **kwargs):
        """Guarda los datos del formulario."""
        data = self.cleaned_data
        data.pop('archivos')
        instance = self.instance

        if instance.pk is None:
            instance = FacturaProveedor.objects.create(**data)
        else:
            FacturaProveedor.objects.filter(pk=instance.pk).update(**data)
            instance = FacturaProveedor.objects.get(pk=instance.pk)

        for f in self.files.getlist('archivos'):
            document = Archivo.objects.create(documento=f)
            instance.archivos.add(document)

        return instance
