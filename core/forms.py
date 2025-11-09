# core/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Nino

class CustomAuthForm(AuthenticationForm):
    # Definir el campo extra que agregaste en el HTML
    tipo_documento = forms.CharField(
        label='Tipo de Documento', 
        widget=forms.Select(choices=[
            ('', 'Seleccione...'),
            ('CC', 'Cédula de Ciudadanía (CC)'),
            ('TI', 'Tarjeta de Identidad (TI)'),
            ('RC', 'Registro Civil (RC)'),
            # Coincidir con las opciones de tu HTML
        ])
    )

    # El campo 'username' es el Número de Documento en tu lógica.
    # Podemos redefinir la etiqueta si es necesario.
    username = forms.CharField(label='Número de Documento', max_length=254)


# ----------------------------------------------------
# 💡 NUEVOS FORMULARIOS PARA EDICIÓN
# ----------------------------------------------------

class AdminPerfilForm(forms.ModelForm):
    """Formulario para que el Administrador edite su perfil."""
    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'email']

class MadrePerfilForm(forms.ModelForm):
    """Formulario para que la Madre Comunitaria edite su perfil."""
    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'email', 'telefono', 'direccion']
        widgets = {
            'nombres': forms.TextInput(attrs={'required': True}),
            'apellidos': forms.TextInput(attrs={'required': True}),
            'email': forms.EmailInput(attrs={'required': True}),
            'telefono': forms.TextInput(attrs={'required': False}),
            'direccion': forms.TextInput(attrs={'required': False}),
        }

class PadrePerfilForm(forms.ModelForm):
    """Formulario para que el Padre de Familia edite su perfil y datos asociados."""
    ocupacion = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'email', 'telefono', 'direccion']
        widgets = {
            'nombres': forms.TextInput(attrs={'required': True}),
            'apellidos': forms.TextInput(attrs={'required': True}),
            'email': forms.EmailInput(attrs={'required': True}),
        }
class NinoForm(forms.ModelForm):
    class Meta:
        model = Nino
        fields = ['nombres', 'apellidos', 'documento', 'fecha_nacimiento', 'genero']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'})
        }

class PadreForm(forms.ModelForm):
    ocupacion = forms.CharField(max_length=50, required=True, label="Ocupación")

    class Meta:
        model = Usuario
        fields = ['documento', 'nombres', 'apellidos', 'email', 'telefono', 'direccion']
        widgets = {
            'telefono': forms.TextInput(attrs={'required': True}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        documento = self.cleaned_data.get('documento')
        # Permitir emails repetidos solo para padres
        if Usuario.objects.filter(email=email, rol__nombre_rol__in=['madre_comunitaria', 'administrador']).exclude(documento=documento).exists():
            raise forms.ValidationError('Este correo ya está registrado para otro usuario que no es padre.')
        return email