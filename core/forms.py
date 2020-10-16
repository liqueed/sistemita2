# -*- coding: utf-8 -*-
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, Layout, HTML, Div, Reset
from django import forms

from .models import Archivo, Cliente, Distrito, Factura, Localidad, MedioPago, Proveedor, OrdenCompra


class MedioPagoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        model = MedioPago
        fields = ('nombre', )


class OrdenCompraForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(
                    Div('fecha', css_class='col-4'),
                    css_class='row'
                ),
                Div(
                    Div('cliente', css_class='col-6'),
                    css_class='row'
                ),
                # Aca va la data extra del cliente por JS
                Div(css_id='info_cliente', css_class='row'),
                Div(
                    Div('moneda', css_class='col-2'),
                    Div('monto', css_class='col-4'),
                    css_class='row'
                ),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'),
                Reset('reset', 'Limpiar', css_class='float-right')
            )
        )

    class Meta:
        model = OrdenCompra
        fields = ('fecha', 'cliente', 'moneda', 'monto')


class FacturaForm(forms.ModelForm):
    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(
                    Div('fecha', css_class='col-4'),
                    css_class='row'
                ),
                Div(
                    Div('cliente', css_class='col-6'),
                    css_class='row'
                ),
                # Aca va la data extra del cliente por JS
                Div(css_id='info_cliente', css_class='row'),
                Div(
                    Div('moneda', css_class='col-2'),
                    Div('monto', css_class='col-4'),
                    css_class='row'
                ),
                Div(
                    Div('cobrado', css_class='col-2'),
                    css_class='row'
                ),
                Div(
                    Div('archivos', css_class='col-2'),
                    css_class='row'
                ),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'),
                Reset('reset', 'Limpiar', css_class='float-right')
            )
        )

    class Meta:
        model = Factura
        fields = ('fecha', 'cliente', 'moneda', 'monto', 'cobrado', 'archivos')

    def save(self, *args, **kwargs):
        data = self.cleaned_data
        data.pop('archivos')

        factura = Factura.objects.create(**data)
        for f in self.files.getlist('archivos'):
            document = Archivo.objects.create(documento=f)
            factura.archivos.add(document)

        return super(FacturaForm, self).save(commit=False)


class ProveedorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'data' in kwargs.keys():
            if 'provincia' in kwargs['data'].keys():
                provincia = kwargs['data'].get('provincia', None)
                if provincia:
                    self.fields['distrito'].queryset = Distrito.objects.filter(provincia=provincia)

            if 'distrito' in kwargs['data'].keys():
                distrito = kwargs['data'].get('distrito', None)
                if distrito:
                    self.fields['localidad'].queryset = Localidad.objects.filter(distrito=distrito)
        else:
            if self.instance and self.instance.provincia:
                self.fields['distrito'].queryset = Distrito.objects.filter(provincia=self.instance.provincia)
            else:
                self.fields['distrito'].queryset = Distrito.objects.none()

            if self.instance and self.instance.distrito:
                self.fields['localidad'].queryset = Localidad.objects.filter(distrito=self.instance.distrito)
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
        model = Proveedor
        fields = (
            'razon_social', 'cuit', 'correo', 'telefono', 'calle', 'numero', 'piso', 'dpto', 'provincia',
            'distrito', 'localidad', 'cbu'
        )


class ClienteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'data' in kwargs.keys():
            if 'provincia' in kwargs['data'].keys():
                provincia = kwargs['data'].get('provincia', None)
                if provincia:
                    self.fields['distrito'].queryset = Distrito.objects.filter(provincia=provincia)

            if 'distrito' in kwargs['data'].keys():
                distrito = kwargs['data'].get('distrito', None)
                if distrito:
                    self.fields['localidad'].queryset = Localidad.objects.filter(distrito=distrito)
        else:
            if self.instance and self.instance.provincia:
                self.fields['distrito'].queryset = Distrito.objects.filter(provincia=self.instance.provincia)
            else:
                self.fields['distrito'].queryset = Distrito.objects.none()

            if self.instance and self.instance.distrito:
                self.fields['localidad'].queryset = Localidad.objects.filter(distrito=self.instance.distrito)
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
                HTML("""<legend>Facturación</legend>"""),
                Div(
                    Div('tipo_envio_factura', css_class='col-2'),
                    Div('correo_envio_factura', css_class='col-5'),
                    Div('link_envio_factura', css_class='col-5'),
                    css_class='row'
                ),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'),
                Reset('reset', 'Limpiar', css_class='float-right')
            )
        )

    class Meta:
        model = Cliente
        fields = (
            'razon_social', 'cuit', 'correo', 'telefono', 'calle', 'numero', 'piso', 'dpto', 'provincia',
            'distrito', 'localidad', 'tipo_envio_factura', 'link_envio_factura', 'correo_envio_factura'
        )
