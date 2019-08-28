from django import forms

class FormSubirArchivoMovimientosBancarios(forms.Form):
    archivo_de_movimientos_bancarios = forms.FileField()