# core/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Nino


# ----------------------------------------------------
# 🟩 FORMULARIO DE LOGIN PERSONALIZADO
# ----------------------------------------------------
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Nino, MadreComunitaria, HogarComunitario # Asegúrate de importar estos modelos
# ... (resto de tus imports)

# --- Formulario de Usuario para la Madre Comunitaria ---
class UsuarioMadreForm(forms.ModelForm):
    # Campos requeridos para la autenticación y base del Usuario
    documento = forms.IntegerField(label='Número de Documento', required=True)
    correo = forms.EmailField(label="Correo electrónico", required=True)
    nombres = forms.CharField(label="Nombres", max_length=50, required=True)
    apellidos = forms.CharField(label="Apellidos", max_length=50, required=True)
    
    class Meta:
        model = Usuario
        # Incluye todos los campos de Usuario que necesitas para el registro
        fields = ['documento', 'tipo_documento', 'nombres', 'apellidos', 'correo', 'telefono', 'direccion']

# --- Formulario del Perfil MadreComunitaria ---
# --- Formulario del Perfil MadreComunitaria ---
class MadreProfileForm(forms.ModelForm):
    class Meta:
        model = MadreComunitaria
        # Incluye todos los campos del perfil de la madre
        exclude = ['usuario', 'fecha_registro'] 
        widgets = {
             # Es crucial listar todos los FileField aquí
             'firma_digital': forms.FileInput(),
             'documento_identidad_pdf': forms.FileInput(),
             'certificado_escolaridad_pdf': forms.FileInput(),
             'certificado_antecedentes_pdf': forms.FileInput(),
             'certificado_medico_pdf': forms.FileInput(),
             'certificado_residencia_pdf': forms.FileInput(),
             'cartas_recomendacion_pdf': forms.FileInput(),
        }
        # --- Formulario de Hogar Comunitario ---
class HogarForm(forms.ModelForm):
    class Meta:
        model = HogarComunitario
        # Excluye el campo 'madre' ya que lo asignaremos en la vista
        exclude = ['madre', 'fecha_registro']

class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(
        label='Número de Documento',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su número de documento',
            'autofocus': True
        })
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )



# ----------------------------------------------------
# 💡 FORMULARIOS DE PERFIL
# ----------------------------------------------------
class AdminPerfilForm(forms.ModelForm):
    """Formulario para que el Administrador edite su perfil."""
    correo = forms.EmailField(label="Correo electrónico", required=True)

    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'correo']


class MadrePerfilForm(forms.ModelForm):
    """Formulario para que la Madre Comunitaria edite su perfil."""
    correo = forms.EmailField(label="Correo electrónico", required=True)

    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'correo', 'telefono', 'direccion']
        widgets = {
            'nombres': forms.TextInput(attrs={'required': True}),
            'apellidos': forms.TextInput(attrs={'required': True}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej. 3001234567'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Ej. Calle 10 #5-25'}),
        }


class PadrePerfilForm(forms.ModelForm):
    """Formulario para que el Padre de Familia edite su perfil."""
    correo = forms.EmailField(label="Correo electrónico", required=True)
    ocupacion = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'correo', 'telefono', 'direccion']
        widgets = {
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej. 3112223344'}),
        }


# ----------------------------------------------------
# 👶 FORMULARIO DE NIÑOS
# ----------------------------------------------------
class NinoForm(forms.ModelForm):
    class Meta:
        model = Nino
        fields = ['nombres', 'apellidos', 'documento', 'fecha_nacimiento', 'genero']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'})
        }


# ----------------------------------------------------
# 👨 FORMULARIO DE REGISTRO DE PADRES
# ----------------------------------------------------
class PadreForm(forms.ModelForm):
    ocupacion = forms.CharField(max_length=50, required=True, label="Ocupación")

    class Meta:
        model = Usuario
        fields = ['documento', 'nombres', 'apellidos', 'correo', 'telefono', 'direccion']
        widgets = {
            'telefono': forms.TextInput(attrs={'required': True}),
        }

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        documento = self.cleaned_data.get('documento')

        if Usuario.objects.filter(correo=correo, rol__nombre_rol__in=['madre_comunitaria', 'administrador']).exclude(documento=documento).exists():
            raise forms.ValidationError('Este correo ya está registrado para otro usuario que no es padre.')
        return correo

    def clean(self):
        cleaned_data = super().clean()
        documento = cleaned_data.get('documento')
        if not documento or not str(documento).isdigit():
            self.add_error('documento', 'El documento debe ser un número válido.')
        return cleaned_data
