"""Formularios del módulo Permission."""

# Django
from django import forms

# Models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# Forms
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, Layout, Div, Reset

User = get_user_model()


class UserCreateForm(forms.ModelForm):
    """Formulario de usuario."""

    def __init__(self, *args, **kwargs):
        """Inicializacion del Formulario."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['groups'].widget.attrs['size'] = 10
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('username', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('first_name', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('last_name', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('email', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('password', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('password_confirmation', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('groups', css_class='col-6'),
                    css_class='row'
                ),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'),
                Reset('reset', 'Limpiar', css_class='float-right')
            )
        )

    username = forms.CharField(min_length=4, max_length=50, label='Nombre de usuario')

    first_name = forms.CharField(min_length=2, max_length=50, label='Nombre')
    last_name = forms.CharField(min_length=2, max_length=50, label='Apellido')

    email = forms.EmailField(min_length=6, max_length=70)

    password = forms.CharField(max_length=70, widget=forms.PasswordInput(), label='Contraseña')

    password_confirmation = forms.CharField(max_length=70, widget=forms.PasswordInput(),
                                            label='Repetir contraseña')

    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), label='Grupos',
                                            required=False)

    def clean_username(self):
        """El nombre de usuario debe ser único."""
        username = self.cleaned_data['username']
        username_taken = User.objects.filter(username=username).exists()

        if username_taken:
            raise forms.ValidationError('El username ya está registrado.')

        return username

    def clean(self):
        """Verifica si las contraseñas coinciden."""
        data = super().clean()
        password = data['password']
        password_confirmation = data['password_confirmation']

        if password != password_confirmation:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        return data

    def save(self):
        """Create user."""
        data = self.cleaned_data
        data.pop('password_confirmation')
        groups = data.pop('groups')

        user = User.objects.create_user(**data)
        if groups:
            user.groups.set(groups)
        user.save()

        return user

    class Meta:
        """Configuraciones del formulario."""

        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'groups')


class UserUpdateForm(forms.ModelForm):
    """Formulario para actualizar datos de usuario."""

    def __init__(self, *args, **kwargs):
        """Inicializacion del Formulario."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['groups'].widget.attrs['size'] = 10
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('username', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('first_name', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('last_name', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('email', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('groups', css_class='col-6'),
                    css_class='row'
                ),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'),
                Reset('reset', 'Limpiar', css_class='float-right')
            )
        )

    first_name = forms.CharField(min_length=2, max_length=50, label='Nombre')
    last_name = forms.CharField(min_length=2, max_length=50, label='Apellido')

    email = forms.EmailField(min_length=6, max_length=70)

    class Meta:
        """Configuraciones del formulario."""

        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'groups')
