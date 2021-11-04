"""Formularios de clientes."""

from re import match

# Django
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Fieldset, Layout, Reset, Submit
from django import forms

# Sistemita
from sistemita.core.models.archivo import Archivo
from sistemita.core.models.cliente import Cliente, Factura, OrdenCompra
from sistemita.core.models.entidad import Distrito, Localidad
from sistemita.core.utils.strings import (
    MESSAGE_CUIT_INVALID,
    MESSAGE_PERMISSION_ERROR,
    MESSAGE_TOTAL_ZERO,
)
from sistemita.expense.models import Fondo


class ClienteForm(forms.ModelForm):
    """Formulario de cliente."""

    correo = forms.CharField(required=True)
    telefono = forms.CharField(required=True)

    def clean_cuit(self):
        """Verifica el cuit."""
        cuit = self.cleaned_data['cuit']
        if not match(r'^[0-9]{11}$', str(cuit)):
            raise forms.ValidationError(MESSAGE_CUIT_INVALID)
        return cuit

    def __init__(self, *args, **kwargs):
        """Inicialización del formulario."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['autocomplete'] = 'off'

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
                Div(Div('razon_social', css_class='col-8'), Div('cuit', css_class='col-4'), css_class='row'),
                Div(Div('correo', css_class='col-6'), Div('telefono', css_class='col-6'), css_class='row'),
                HTML("""<legend>Dirección</legend>"""),
                Div(
                    Div('calle', css_class='col-6'),
                    Div('numero', css_class='col-2'),
                    Div('piso', css_class='col-2'),
                    Div('dpto', css_class='col-2'),
                    css_class='row',
                ),
                Div(
                    Div('provincia', css_class='col-4'),
                    Div('distrito', css_class='col-4'),
                    Div('localidad', css_class='col-4'),
                    css_class='row',
                ),
                HTML("""<legend>Facturación</legend>"""),
                Div(
                    Div('tipo_envio_factura', css_class='col-2'),
                    Div('correo_envio_factura', css_class='col-5'),
                    Div('link_envio_factura', css_class='col-5'),
                    css_class='row',
                ),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'), Reset('reset', 'Limpiar', css_class='float-right')
            ),
        )

    class Meta:
        """Configuraciones del formulario."""

        model = Cliente
        fields = (
            'razon_social',
            'cuit',
            'correo',
            'telefono',
            'calle',
            'numero',
            'piso',
            'dpto',
            'provincia',
            'distrito',
            'localidad',
            'tipo_envio_factura',
            'link_envio_factura',
            'correo_envio_factura',
        )


class FacturaForm(forms.ModelForm):
    """Formuarlio de Facturación a cliente."""

    neto = forms.DecimalField(initial=0.0, decimal_places=2, max_digits=12)

    def __init__(self, *args, **kwargs):
        """Inicialización de formulario."""
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['autocomplete'] = 'off'

        # Permisos
        if not self.user.has_perm('core.change_nro_factura'):
            self.fields['numero'].widget.attrs['readonly'] = True
        if not self.user.has_perm('core.change_neto_factura'):
            self.fields['moneda'].widget.attrs['readonly'] = True
            self.fields['neto'].widget.attrs['readonly'] = True
        if not self.user.has_perm('core.change_iva_factura'):
            self.fields['iva'].widget.attrs['readonly'] = True
        if not self.user.has_perm('core.change_total_factura'):
            self.fields['total'].widget.attrs['readonly'] = True

        self.fields['numero'].label = 'Número de factura'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(Div('fecha', css_class='col-4'), css_class='row'),
                Div(Div('numero', css_class='col-4'), Div('tipo', css_class='col-2'), css_class='row'),
                Div(Div('cliente', css_class='col-6'), css_class='row'),
                # Aca va la data extra del cliente por JS
                Div(css_id='info_cliente', css_class='row'),
                Div(Div('detalle', css_class='col-6'), css_class='row'),
                Div(Div('moneda', css_class='col-2'), Div('neto', css_class='col-4'), css_class='row'),
                Div(Div('iva', css_class='col-2'), css_class='row'),
                Div(Div('total', css_class='col-4'), css_class='row'),
                Div(Div('cobrado', css_class='col-2'), css_class='row'),
                Div(Div('archivos', template='components/input_files.html'), css_class='row'),
                Div(css_id='adjuntos', css_class='row'),
                Div(Div('porcentaje_fondo', css_class='col-2'), css_class='row'),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'), Reset('reset', 'Limpiar', css_class='float-right')
            ),
        )

    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    class Meta:
        """Configuraciones del formulario."""

        model = Factura
        fields = (
            'numero',
            'tipo',
            'fecha',
            'cliente',
            'detalle',
            'moneda',
            'iva',
            'neto',
            'total',
            'cobrado',
            'archivos',
            'porcentaje_fondo',
        )

    def clean_numero(self):
        """Verifica si el usuario tiene permisos para editar el campo."""
        numero = self.cleaned_data['numero']
        if not self.user.has_perm('core.change_nro_factura'):
            if self.instance.numero != numero:
                raise forms.ValidationError(MESSAGE_PERMISSION_ERROR)
        return numero

    def clean_moneda(self):
        """Verifica si el usuario tiene permisos para editar el campo."""
        moneda = self.cleaned_data['moneda']
        if not self.user.has_perm('core.change_neto_factura'):
            if self.instance.moneda != moneda:
                raise forms.ValidationError(MESSAGE_PERMISSION_ERROR)
        return moneda

    def clean_neto(self):
        """Verifica si el usuario tiene permisos para editar el campo."""
        neto = self.cleaned_data['neto']
        if not self.user.has_perm('core.change_neto_factura'):
            if neto not in [self.fields['neto'].initial, self.instance.neto]:
                raise forms.ValidationError(MESSAGE_PERMISSION_ERROR)
        return neto

    def clean_iva(self):
        """Verifica si el usuario tiene permisos para editar el campo."""
        iva = self.cleaned_data['iva']
        if not self.user.has_perm('core.change_iva_factura'):
            if self.fields['iva'].initial != iva:
                raise forms.ValidationError(MESSAGE_PERMISSION_ERROR)
        return iva

    def clean_total(self):
        """Verifica si el usuario tiene permisos para editar el campo."""
        total = self.cleaned_data['total']

        if not self.user.has_perm('core.change_total_factura'):
            # Verifico que el total calculado no haya sido modificado
            neto = float(self.instance.neto)
            total_calculado = neto + (self.instance.iva / 100) * neto
            if total_calculado != float(total):
                raise forms.ValidationError(MESSAGE_PERMISSION_ERROR)
        if total == 0:
            raise forms.ValidationError(MESSAGE_TOTAL_ZERO)

        return total

    def clean_archivos(self):
        """Verifica si el usuario tiene permisos para editar el campo."""
        archivos = self.files.getlist('archivos')
        if not self.user.has_perm('core.change_archivos_factura'):
            if archivos:
                raise forms.ValidationError(MESSAGE_PERMISSION_ERROR)
        return archivos

    def save(self, commit=True):
        """Guarda los datos recibidos del formulario."""
        data = self.cleaned_data
        data.pop('archivos')
        instance = self.instance

        if instance.pk is None:
            instance = Factura.objects.create(**data)
            Fondo.objects.create(
                factura=instance,
                monto=instance.porcentaje_fondo_monto,
                monto_disponible=instance.porcentaje_fondo_monto,
                disponible=instance.cobrado
            )
        else:
            Factura.objects.filter(pk=instance.pk).update(**data)
            instance = Factura.objects.get(pk=instance.pk)
            instance.factura_fondo.update(
                moneda=instance.moneda,
                monto=instance.porcentaje_fondo_monto,
                monto_disponible=instance.porcentaje_fondo_monto,
                disponible=instance.cobrado
            )

        for f in self.files.getlist('archivos'):
            document = Archivo.objects.create(documento=f)
            instance.archivos.add(document)

        return instance


class OrdenCompraForm(forms.ModelForm):
    """Formulario de orden de compra."""

    def __init__(self, *args, **kwargs):
        """Inicialización del formulario."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['autocomplete'] = 'off'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(Div('fecha', css_class='col-4'), css_class='row'),
                Div(Div('cliente', css_class='col-6'), css_class='row'),
                # Aca va la data extra del cliente por JS
                Div(css_id='info_cliente', css_class='row'),
                Div(Div('moneda', css_class='col-2'), Div('monto', css_class='col-4'), css_class='row'),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'), Reset('reset', 'Limpiar', css_class='float-right')
            ),
        )

    class Meta:
        """Configuraciones del formulario."""

        model = OrdenCompra
        fields = ('fecha', 'cliente', 'moneda', 'monto')
