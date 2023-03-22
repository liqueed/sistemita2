"""Formularios de clientes."""

# Utils
from decimal import Decimal
from re import match

# Django
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Fieldset, Layout, Reset, Submit
from django import forms
from django.contrib import admin
from django_select2 import forms as ds2_forms

# Sistemita
from sistemita.core.models.archivo import Archivo
from sistemita.core.models.cliente import (
    Cliente,
    Contrato,
    Factura,
    FacturaCategoria,
    FacturaDistribuida,
)
from sistemita.core.models.entidad import Distrito, Localidad
from sistemita.core.models.proveedor import Proveedor
from sistemita.expense.models import Fondo
from sistemita.utils.commons import get_porcentaje_agregado
from sistemita.utils.strings import (
    MESSAGE_CUIT_INVALID,
    MESSAGE_PERMISSION_ERROR,
    MESSAGE_TOTAL_INVALID,
    MESSAGE_TOTAL_ZERO,
)

admin.autodiscover()


class ClienteForm(forms.ModelForm):
    """Formulario de cliente."""

    razon_social = forms.CharField(required=True)
    cuit = forms.CharField(required=True, max_length=11)
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

    def __init__(self, *args, **kwargs):
        """Inicialización de formulario."""
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['autocomplete'] = 'off'

        self.fields['monto_imputado'].widget.attrs['readonly'] = True
        # Permisos
        if not self.user.has_perm('core.change_nro_factura'):
            self.fields['numero'].widget.attrs['readonly'] = True
        if not self.user.has_perm('core.change_moneda_factura'):
            self.fields['moneda'].widget.attrs['readonly'] = True
        if not self.user.has_perm('core.change_neto_factura'):
            self.fields['neto'].widget.attrs['readonly'] = True
        if not self.user.has_perm('core.change_iva_factura'):
            self.fields['iva'].widget.attrs['readonly'] = True
        if not self.user.has_perm('core.change_total_factura'):
            self.fields['total'].widget.attrs['readonly'] = True

        self.fields['numero'].label = 'Número de factura'
        self.fields['proveedores'].label = 'Coachs de la iniciativa'
        self.fields['fecha_estimada_pago'].label = 'Fecha estimada de pago'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(Div('fecha', css_class='col-4'), css_class='row'),
                Div(Div('fecha_estimada_pago', css_class='col-4'), css_class='row'),
                Div(Div('numero', css_class='col-4'), Div('tipo', css_class='col-2'), css_class='row'),
                Div(Div('contrato', css_class='col-4'), css_class='row'),
                Div(Div('categoria', css_class='col-4'), css_class='row'),
                Div(Div('cliente', css_class='col-6'), css_class='row'),
                Div(Div('proveedores', css_class='col-6'), css_class='row'),
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
                Div(Div('porcentaje_socio_alan', css_class='col-2'), css_class='row'),
                Div(Div('porcentaje_socio_ariel', css_class='col-2'), css_class='row'),
                Div(Div('monto_imputado', css_class='col-2'), css_class='row'),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'), Reset('reset', 'Limpiar', css_class='float-right')
            ),
        )

    neto = forms.DecimalField(initial=0.0, decimal_places=2, max_digits=12)
    archivos = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    proveedores = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Proveedor.objects.all(),
        widget=ds2_forms.ModelSelect2MultipleWidget(
            model=Proveedor,
            search_fields=['razon_social__icontains'],
            # dependent_fields={'territories': 'continent_name__icontains'},
            max_results=500,
            attrs={"class": "form-control"},
        ),
    )

    class Meta:
        """Configuraciones del formulario."""

        model = Factura
        widgets = {'name_of_manytomanyfield': forms.widgets.CheckboxSelectMultiple()}
        fields = (
            'numero',
            'tipo',
            'fecha',
            'fecha_estimada_pago',
            'cliente',
            'proveedores',
            'detalle',
            'moneda',
            'iva',
            'neto',
            'total',
            'cobrado',
            'archivos',
            'porcentaje_fondo',
            'porcentaje_socio_alan',
            'porcentaje_socio_ariel',
            'monto_imputado',
            'categoria',
            'contrato',
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
        if not self.user.has_perm('core.change_moneda_factura'):
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

        total = self.cleaned_data.get('total', None)
        neto = self.cleaned_data.get('neto', None)
        iva = self.cleaned_data.get('iva', None)

        # Verifico que el total calculado no haya sido modificado
        if not self.user.has_perm('core.change_total_factura'):
            neto = float(self.instance.neto)
            total_calculado = get_porcentaje_agregado(amount=neto, percentage=self.instance.iva)
            if total_calculado != float(total):
                raise forms.ValidationError(MESSAGE_PERMISSION_ERROR)

        if total == 0:
            raise forms.ValidationError(MESSAGE_TOTAL_ZERO)

        if total and neto and iva:
            if total != get_porcentaje_agregado(amount=neto, percentage=iva):
                raise forms.ValidationError(MESSAGE_TOTAL_INVALID)

        return total

    def clean_archivos(self):
        """Verifica si el usuario tiene permisos para editar el campo."""
        archivos = self.files.getlist('archivos')
        if not self.user.has_perm('core.change_archivos_factura'):
            if archivos:
                raise forms.ValidationError(MESSAGE_PERMISSION_ERROR)
        return archivos

    def clean(self):
        """Valida los porcentajes de los socios."""
        data = super().clean()
        porcentajes = data.get('porcentaje_socio_ariel', 0) + data.get('porcentaje_socio_alan', 0)

        if porcentajes > 100:
            raise forms.ValidationError('Los porcentaje de socios no pueden superar el 100%.')

        return self.cleaned_data

    def save(self, commit=True):
        """Guarda los datos recibidos del formulario."""
        data = self.cleaned_data
        data.pop('archivos')
        proveedores = data.pop('proveedores')
        instance = self.instance

        if instance.pk is None:
            instance = Factura.objects.create(**data)
            Fondo.objects.create(
                factura=instance,
                monto=instance.porcentaje_fondo_monto,
                monto_disponible=instance.porcentaje_fondo_monto,
                disponible=instance.cobrado,
                moneda=instance.moneda,
            )
        else:
            Factura.objects.filter(pk=instance.pk).update(**data)
            instance.factura_fondo.update_or_create(
                moneda=instance.moneda,
                monto=instance.porcentaje_fondo_monto,
                monto_disponible=instance.porcentaje_fondo_monto,
                disponible=instance.cobrado,
            )

        if proveedores:
            instance.proveedores.clear()
            for proveedor in proveedores:
                instance.proveedores.add(proveedor)

        for f in self.files.getlist('archivos'):
            document = Archivo.objects.create(documento=f)
            instance.archivos.add(document)

        if not hasattr(instance, 'factura_distribuida'):
            FacturaDistribuida.objects.create(factura=instance)
        else:
            facturadistribuida = FacturaDistribuida.objects.get(factura=instance)
            if (
                round(Decimal(facturadistribuida.monto_distribuido), 2)
                == instance.monto_neto_sin_fondo_porcentaje_socios
            ):
                facturadistribuida.distribuida = True
                facturadistribuida.save()

        return instance


class ContratoForm(forms.ModelForm):
    """Formulario del modelo Contrato."""

    monto = forms.DecimalField(decimal_places=2, max_digits=12, min_value=0, initial=0.0)
    proveedores = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Proveedor.objects.all(),
        widget=ds2_forms.ModelSelect2MultipleWidget(
            model=Proveedor,
            search_fields=['razon_social__icontains'],
            # dependent_fields={'territories': 'continent_name__icontains'},
            max_results=500,
            attrs={"class": "form-control"},
        ),
    )

    def __init__(self, *args, **kwargs):
        """Inicialización del formulario."""
        super().__init__(*args, **kwargs)
        self.fields['proveedores'].label = 'Coachs que interactúan'
        self.fields['categoria'].label = 'Categoría'

        for field in self.fields.values():
            field.widget.attrs['autocomplete'] = 'off'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(Div('fecha_desde', css_class='col-4'), css_class='row'),
                Div(Div('fecha_hasta', css_class='col-4'), css_class='row'),
                Div(Div('categoria', css_class='col-6'), css_class='row'),
                Div(Div('cliente', css_class='col-6'), css_class='row'),
                # Aca va la data extra del cliente por JS
                Div(css_id='info_cliente', css_class='row'),
                Div(Div('proveedores', css_class='col-6'), css_class='row'),
                Div(Div('detalle', css_class='col-4'), css_class='row'),
                Div(Div('moneda', css_class='col-2'), Div('monto', css_class='col-4'), css_class='row'),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'), Reset('reset', 'Limpiar', css_class='float-right')
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        if fecha_desde and fecha_hasta:
            if fecha_desde > fecha_hasta:
                raise forms.ValidationError('La fecha desde no puede ser mayor que la fecha hasta')

        return cleaned_data

    class Meta:
        """Configuraciones del formulario."""

        model = Contrato
        fields = ('fecha_desde', 'fecha_hasta', 'categoria', 'cliente', 'detalle', 'proveedores', 'moneda', 'monto')


class FacturaCategoriaForm(forms.ModelForm):
    """Formulario de Categoría de factura."""

    def __init__(self, *args, **kwargs):
        """Inicialización del formulario."""
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['autocomplete'] = 'off'
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Datos generales',
                Div(Div('nombre', css_class='col-4'), css_class='row'),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'), Reset('reset', 'Limpiar', css_class='float-right')
            ),
        )

    class Meta:
        """Configuraciones del formulario."""

        model = FacturaCategoria
        fields = ('nombre',)
