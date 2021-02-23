"""Formularios del módulo Permission."""

# Django
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import password_validation
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# Forms
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Fieldset, Layout, Reset, Submit

# Utils
from core.utils.strings import HELP_TEXT_MULTIPLE_CHOICE, HELP_TEXT_PASSWORD_CONFIRMATION, HELP_TEXT_USERNAME

User = get_user_model()


class UserCreateForm(forms.ModelForm):
    """Formulario de usuario."""

    def __init__(self, *args, **kwargs):
        """Inicializacion del Formulario."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['is_superuser'].widget.attrs['checked'] = False
        self.fields['groups'].widget.attrs['size'] = 10
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('first_name', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('last_name', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('username', css_class='col-6'),
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
                    Div('is_superuser', css_class='col-6'),
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

    username = forms.CharField(
        min_length=4,
        max_length=50,
        label='Nombre de usuario',
        validators=[UnicodeUsernameValidator],
        help_text=HELP_TEXT_USERNAME.format(50)
    )

    email = forms.EmailField(min_length=6, max_length=70)

    password = forms.CharField(
        max_length=70,
        widget=forms.PasswordInput(),
        label='Contraseña',
        help_text=password_validation.password_validators_help_text_html
    )
    password_confirmation = forms.CharField(
        max_length=70,
        widget=forms.PasswordInput(),
        label='Repetir contraseña',
        help_text=HELP_TEXT_PASSWORD_CONFIRMATION
    )

    is_superuser = forms.BooleanField(required=False, label='Administrador')
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.order_by('name'),
        help_text=HELP_TEXT_MULTIPLE_CHOICE,
        label='Grupos',
        required=False
    )

    def clean_username(self):
        """El nombre de usuario debe ser único."""
        username = self.cleaned_data['username']
        username_taken = User.objects.filter(username=username).exists()

        if username_taken:
            raise forms.ValidationError('El username ya está registrado.')

        return username

    def clean_email(self):
        """El email debe ser único y con el formato válido."""
        email = self.cleaned_data['email']
        email_taken = User.objects.filter(email=email).exists()

        if email_taken:
            raise forms.ValidationError('El email ya está registrado.')

        try:
            validate_email(email)
        except ValidationError as error:
            raise forms.ValidationError(error)

        return email

    def clean(self):
        """Verifica si las contraseñas coinciden y tienen el formato válido."""
        data = super().clean()
        password = data['password']

        try:
            validate_password(password)
        except ValidationError as error:
            raise forms.ValidationError(error)

        password_confirmation = data['password_confirmation']

        if password != password_confirmation:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        return data

    def save(self, commit=True):
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
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'groups')


class ReadOnlyPasswordWidget(forms.Widget):
    """Widget para mostrar un campo con una contraseña dummy."""

    template_name = 'widgets/read_only_password.html'
    read_only = True


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
                    Div('first_name', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('last_name', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('username', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('email', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('password_read_only', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('is_superuser', css_class='col-6'),
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

    password_read_only = forms.CharField(
        widget=ReadOnlyPasswordWidget,
        required=False,
        label='Contraseña',
        help_text=("Para cambiar la contraseña usar <a href=\"../password/\">este formulario</a>.")
    )

    is_superuser = forms.BooleanField(required=False, label='Administrador')

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.order_by('name'),
        help_text=HELP_TEXT_MULTIPLE_CHOICE,
        label='Grupos',
        required=False
    )

    class Meta:
        """Configuraciones del formulario."""

        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'is_superuser', 'groups')


class PasswordResetForm(SetPasswordForm):
    """Fomulario para resetear contraseña de un usuario."""

    def __init__(self, *args, **kwargs):
        """Inicializacion del Formulario."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                Div(
                    Div('new_password1', css_class='col-6'),
                    css_class='row'
                ),
                Div(
                    Div('new_password2', css_class='col-6'),
                    css_class='row'
                ),
            ),
            FormActions(
                Submit('submit', 'Guardar', css_class='float-right'),
                Reset('reset', 'Limpiar', css_class='float-right')
            )
        )
