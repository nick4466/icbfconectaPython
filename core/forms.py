# core/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from .models import Usuario, Nino, MadreComunitaria, HogarComunitario, Regional, Ciudad


# ----------------------------------------------------
# 🟩 FORMULARIO DE LOGIN PERSONALIZADO
# ----------------------------------------------------
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Nino, MadreComunitaria, HogarComunitario, Regional # Asegúrate de importar estos modelos
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
class MadreProfileForm(forms.ModelForm):
    foto_madre = forms.ImageField(label="Foto de la Madre", required=True, widget=forms.FileInput(attrs={'accept': 'image/*'}))

    class Meta:
        model = MadreComunitaria
        # Incluye todos los campos del perfil de la madre
        exclude = ['usuario', 'fecha_registro']
        widgets = {
             # Es crucial listar todos los FileField aquí
             'foto_madre': forms.FileInput(),
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
    regional = forms.ModelChoiceField(
        queryset=Regional.objects.all(),
        required=True,
        label="Regional",
        widget=forms.Select,
        empty_label="-- Seleccione una Regional --"
    )
    ciudad = forms.ModelChoiceField(
        queryset=Ciudad.objects.none(),
        required=True,
        label="Ciudad",
        widget=forms.Select,
        empty_label="-- Seleccione una Ciudad --"
    )

    class Meta:
        model = HogarComunitario
        fields = ['regional', 'ciudad', 'direccion', 'localidad']  # Ajusta según los campos reales del modelo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'regional' in self.data:
            try:
                regional_id = int(self.data.get('regional'))
                self.fields['ciudad'].queryset = Ciudad.objects.filter(regional_id=regional_id).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['ciudad'].queryset = Ciudad.objects.none()
        elif self.instance and self.instance.pk and self.instance.regional:
            self.fields['ciudad'].queryset = Ciudad.objects.filter(regional=self.instance.regional).order_by('nombre')
        else:
            self.fields['ciudad'].queryset = Ciudad.objects.none()

# ----------------------------------------------------
# 💡 NUEVO: Formulario para Administradores
# ----------------------------------------------------
class AdminForm(forms.ModelForm):
    contraseña = forms.CharField(widget=forms.PasswordInput, required=False, label="Nueva Contraseña")
    foto_admin = forms.ImageField(label="Foto de Perfil", required=False, widget=forms.FileInput(attrs={'accept': 'image/*'}))

    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'documento', 'correo', 'foto_admin', 'contraseña']


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
# 🟩 FORMULARIO DE RESETEO DE CONTRASEÑA
# ----------------------------------------------------
class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

    def clean_email(self):
        """
        Valida que el correo electrónico exista en la base de datos para un usuario activo.
        """
        email = self.cleaned_data.get("email")
        # Usamos list() para ejecutar la consulta y ver si hay resultados.
        if not list(self.get_users(email)):
            raise forms.ValidationError("No existe un usuario activo registrado con ese correo electrónico.")
        return email

    def get_users(self, email):
        """
        Sobrescribimos este método porque nuestro modelo Usuario usa 'correo' en lugar de 'email'.
        Busca usuarios activos que coincidan con el correo proporcionado.
        """
        active_users = Usuario._default_manager.filter(correo__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())


# ----------------------------------------------------
# 💡 FORMULARIOS DE PERFIL
# ----------------------------------------------------
class AdminPerfilForm(forms.ModelForm):
    """Formulario para que el Administrador edite su perfil."""
    correo = forms.EmailField(label="Correo electrónico", required=True)
    foto_admin = forms.ImageField(label="Foto de Perfil", required=False, widget=forms.FileInput(attrs={'accept': 'image/*'}))

    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'correo', 'foto_admin']


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

        # Si el formulario está ligado a una instancia (edición), el chequeo es diferente
        if self.instance and self.instance.pk:
            if Usuario.objects.filter(correo=correo).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este correo ya está en uso por otro usuario.')
        # Si es un formulario de creación y el correo ya existe
        elif not self.instance.pk and Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError('Este correo ya está registrado. Si es el mismo padre, usa su número de documento para cargarlo.')
        return correo

    def clean(self):
        cleaned_data = super().clean()
        documento = cleaned_data.get('documento')
        if not documento or not str(documento).isdigit():
            self.add_error('documento', 'El documento debe ser un número válido.')
        return cleaned_data
