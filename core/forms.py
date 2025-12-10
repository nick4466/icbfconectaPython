# core/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from .models import (Usuario, Nino, MadreComunitaria, HogarComunitario, Regional, Ciudad, Discapacidad,
                     Departamento, Municipio, LocalidadBogota, VisitaTecnica, ActaVisitaTecnica,
                     ConvivienteHogar)


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
    # Opciones de tipo de documento específicas para Agente Educativo (sin Tarjeta de identidad)
    TIPO_DOC_AGENTE_CHOICES = [
        ('CC', 'Cédula de ciudadanía'),
        ('CE', 'Cédula de extranjería'),
        ('PA', 'Pasaporte'),
    ]
    
    # Campos requeridos para la autenticación y base del Usuario
    tipo_documento = forms.ChoiceField(
        choices=TIPO_DOC_AGENTE_CHOICES,
        label='Tipo de Documento',
        required=True,
        initial='CC'
    )
    documento = forms.IntegerField(label='Número de Documento', required=True)
    correo = forms.EmailField(label="Correo electrónico", required=True)
    nombres = forms.CharField(label="Nombres", max_length=50, required=True)
    apellidos = forms.CharField(label="Apellidos", max_length=50, required=True)
    fecha_nacimiento = forms.DateField(
        label="Fecha de Nacimiento",
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="El agente educativo debe tener entre 20 y 45 años de edad"
    )
    sexo = forms.ChoiceField(
        label="Sexo",
        choices=[
            ('M', 'Masculino'),
            ('F', 'Femenino'),
            ('O', 'Otro'),
        ],
        initial='F',
        required=True,
        widget=forms.RadioSelect
    )
    
    # 🆕 Campos geográficos
    departamento_residencia = forms.ModelChoiceField(
        queryset=Departamento.objects.all().order_by('nombre'),
        required=True,
        label="Departamento de Residencia",
        empty_label="-- Seleccione un Departamento --"
    )
    ciudad_residencia = forms.ModelChoiceField(
        queryset=Municipio.objects.none(),
        required=True,
        label="Ciudad/Municipio de Residencia",
        empty_label="-- Seleccione una Ciudad --"
    )
    localidad_bogota = forms.ModelChoiceField(
        queryset=LocalidadBogota.objects.all().order_by('numero'),
        required=False,
        label="Localidad (solo Bogotá)",
        empty_label="-- Seleccione una Localidad --"
    )
    
    class Meta:
        model = Usuario
        fields = ['documento', 'tipo_documento', 'nombres', 'apellidos', 'fecha_nacimiento', 'sexo', 'correo', 'telefono',
                  'departamento_residencia', 'ciudad_residencia', 'localidad_bogota', 'direccion', 'barrio']
    
    def clean_fecha_nacimiento(self):
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            hoy = date.today()
            edad = relativedelta(hoy, fecha_nacimiento).years
            
            if edad < 20:
                raise forms.ValidationError(
                    f'El agente educativo debe tener al menos 20 años de edad. Edad actual: {edad} años.'
                )
            elif edad > 45:
                raise forms.ValidationError(
                    f'El agente educativo no puede tener más de 45 años de edad. Edad actual: {edad} años.'
                )
        
        return fecha_nacimiento
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar municipios si hay departamento seleccionado
        if 'departamento_residencia' in self.data:
            try:
                departamento_id = int(self.data.get('departamento_residencia'))
                self.fields['ciudad_residencia'].queryset = Municipio.objects.filter(
                    departamento_id=departamento_id
                ).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['ciudad_residencia'].queryset = Municipio.objects.none()
        elif self.instance.pk and self.instance.departamento_residencia:
            self.fields['ciudad_residencia'].queryset = Municipio.objects.filter(
                departamento=self.instance.departamento_residencia
            ).order_by('nombre')

# --- Formulario del Perfil MadreComunitaria ---
class MadreProfileForm(forms.ModelForm):
    # Permitir imágenes y PDFs para foto y firma
    foto_madre = forms.FileField(
        label="Foto de la Madre", 
        required=True, 
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )
    firma_digital = forms.FileField(
        label="Firma Digital",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )

    class Meta:
        model = MadreComunitaria
        # Incluye todos los campos del perfil de la madre
        exclude = ['usuario', 'fecha_registro']
        widgets = {
             # Aceptar PDFs e imágenes en todos los campos de archivos
             'foto_madre': forms.FileInput(attrs={'accept': 'image/*,application/pdf'}),
             'firma_digital': forms.FileInput(attrs={'accept': 'image/*,application/pdf'}),
             'certificado_laboral': forms.FileInput(attrs={'accept': 'application/pdf,image/*'}),
             'carta_disponibilidad': forms.FileInput(attrs={'accept': 'application/pdf,image/*'}),
             'documento_identidad_pdf': forms.FileInput(attrs={'accept': 'application/pdf,image/*'}),
             'certificado_escolaridad_pdf': forms.FileInput(attrs={'accept': 'application/pdf,image/*'}),
             'certificado_antecedentes_pdf': forms.FileInput(attrs={'accept': 'application/pdf,image/*'}),
             'certificado_medico_pdf': forms.FileInput(attrs={'accept': 'application/pdf,image/*'}),
             'certificado_residencia_pdf': forms.FileInput(attrs={'accept': 'application/pdf,image/*'}),
             'cartas_recomendacion_pdf': forms.FileInput(attrs={'accept': 'application/pdf,image/*'}),
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
    localidad_bogota = forms.ModelChoiceField(
        queryset=LocalidadBogota.objects.all().order_by('nombre'),
        required=False,
        label="Localidad (solo para Bogotá)",
        widget=forms.Select(attrs={'id': 'id_localidad_hogar'}),
        empty_label="-- Seleccione una Localidad --"
    )

    class Meta:
        model = HogarComunitario
        # Excluir campos que se asignan manualmente en la vista o automáticamente
        exclude = ['localidad', 'madre', 'fecha_registro', 'fecha_habilitacion', 
                   'area_social_m2', 'capacidad_calculada', 'formulario_completo']
        labels = {
            'nombre_hogar': 'Nombre del Hogar Comunitario',
            'direccion': 'Dirección Completa',
            'localidad_bogota': 'Localidad (solo Bogotá)',
            'barrio': 'Barrio',
            'estrato': 'Estrato Socioeconómico',
            'num_habitaciones': 'Número de Habitaciones',
            'num_banos': 'Número de Baños',
            'material_construccion': 'Material de Construcción',
            'riesgos_cercanos': 'Riesgos Cercanos al Hogar',
            'fotos_interior': 'Fotos del Interior',
            'fotos_exterior': 'Fotos del Exterior',
            'geolocalizacion_lat': 'Latitud',
            'geolocalizacion_lon': 'Longitud',
            'tipo_tenencia': 'Tipo de Tenencia del Inmueble',
            'documento_tenencia_pdf': 'Documento de Tenencia (PDF)',
            'capacidad_maxima': 'Capacidad Máxima de Niños',
            'estado': 'Estado del Hogar',
        }
        widgets = {
            'fotos_interior': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'fotos_exterior': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'documento_tenencia_pdf': forms.FileInput(attrs={'accept': 'application/pdf', 'class': 'form-control'}),
            'riesgos_cercanos': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ej: Cerca de vías principales, zona de inundación, etc.', 'class': 'form-control'}),
            'material_construccion': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ej: Ladrillo, concreto, madera, etc.', 'class': 'form-control'}),
            'geolocalizacion_lat': forms.NumberInput(attrs={'step': '0.0000001', 'placeholder': 'Ej: 4.6097100', 'class': 'form-control'}),
            'geolocalizacion_lon': forms.NumberInput(attrs={'step': '0.0000001', 'placeholder': 'Ej: -74.0817500', 'class': 'form-control'}),
            'nombre_hogar': forms.TextInput(attrs={'placeholder': 'Ej: Hogar Comunitario Los Ángeles', 'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Ej: Cra 97#135a-30 SUBA', 'id': 'id_direccion_hogar', 'class': 'form-control'}),
            'barrio': forms.TextInput(attrs={'placeholder': 'Ej: El Poblado, Chapinero, etc.', 'class': 'form-control'}),
            'estrato': forms.NumberInput(attrs={'min': 1, 'max': 6, 'class': 'form-control'}),
            'num_habitaciones': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'num_banos': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'capacidad_maxima': forms.NumberInput(attrs={'min': 1, 'max': 30, 'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'tipo_tenencia': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'geolocalizacion_lat': 'Coordenada de latitud (opcional, use Google Maps para obtenerla)',
            'geolocalizacion_lon': 'Coordenada de longitud (opcional, use Google Maps para obtenerla)',
            'capacidad_maxima': 'Número máximo de niños que puede atender el hogar (por defecto 15)',
            'tipo_tenencia': 'Indique si el inmueble es propio, arrendado o en comodato',
            'fotos_interior': 'Suba fotos del interior del hogar (opcional)',
            'fotos_exterior': 'Suba fotos del exterior del hogar (opcional)',
            'documento_tenencia_pdf': 'Documento que acredite la tenencia del inmueble (opcional)',
            'direccion': 'Ingrese la dirección completa del hogar (será verificada con la localidad)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Establecer estado por defecto en "Pendiente de Visita" para nuevos hogares
        if not self.instance.pk:  # Solo para creación, no para edición
            self.fields['estado'].initial = 'pendiente_visita'
            # Hacer el campo NO requerido para que no falle la validación si no se envía
            self.fields['estado'].required = False
            # Aplicar estilo visual de deshabilitado
            self.fields['estado'].widget.attrs['style'] = 'pointer-events: none; background-color: #e9ecef;'
            self.fields['estado'].help_text = 'El estado inicial siempre es "Pendiente de Visita"'
            # Hacer que el campo capacidad_maxima también sea no requerido para nuevos hogares
            self.fields['capacidad_maxima'].required = False
            self.fields['capacidad_maxima'].initial = 15  # Usar el valor por defecto del modelo
            self.fields['capacidad_maxima'].widget.attrs['style'] = 'pointer-events: none; background-color: #e9ecef;'
            self.fields['capacidad_maxima'].help_text = 'La capacidad se determinará después de la visita técnica'
        
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
    
    def clean_estado(self):
        """Asegurar que nuevos hogares siempre tengan estado 'pendiente_visita'"""
        if not self.instance.pk:  # Solo para nuevos hogares
            return 'pendiente_visita'
        # Para hogares existentes, devolver el valor del formulario o mantener el actual
        estado = self.cleaned_data.get('estado')
        return estado if estado else self.instance.estado
    
    def clean_capacidad_maxima(self):
        """Para nuevos hogares, usar el valor por defecto (15) hasta la visita técnica"""
        if not self.instance.pk:  # Solo para nuevos hogares
            return 15  # Valor por defecto del modelo
        # Para hogares existentes, devolver el valor del formulario
        capacidad = self.cleaned_data.get('capacidad_maxima')
        return capacidad if capacidad is not None else 15
    
    def clean(self):
        cleaned_data = super().clean()
        ciudad = cleaned_data.get('ciudad')
        localidad_bogota = cleaned_data.get('localidad_bogota')
        direccion = cleaned_data.get('direccion')
        
        # Forzar estado pendiente_visita para nuevos hogares
        if not self.instance.pk:
            cleaned_data['estado'] = 'pendiente_visita'
        
        # Si la ciudad es Bogotá, validar que se seleccione una localidad
        if ciudad and ciudad.nombre.upper() == 'BOGOTÁ':
            if not localidad_bogota:
                self.add_error('localidad_bogota', 'Debe seleccionar una localidad para hogares en Bogotá')
        
        # Si hay localidad seleccionada y dirección, validar coherencia (validación básica)
        if localidad_bogota and direccion:
            # Aquí se puede implementar lógica más sofisticada de validación
            # Por ahora, solo verificamos que se hayan proporcionado ambos campos
            pass
        
        return cleaned_data

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
    foto_admin = forms.ImageField(label="Foto de Perfil", required=False, widget=forms.FileInput(attrs={'accept': 'image/*'}))

    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'correo', 'telefono', 'direccion', 'foto_admin']
        widgets = {
            'telefono': forms.TextInput(attrs={'placeholder': 'Ej. 3112223344'}),
        }


# ----------------------------------------------------
# 👶 FORMULARIO DE NIÑOS (Expandido)
# ----------------------------------------------------
class NinoForm(forms.ModelForm):
    foto = forms.ImageField(
        label="Foto del Niño",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    carnet_vacunacion = forms.FileField(
        label="Carné de Vacunación",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )
    certificado_eps = forms.FileField(
        label="Certificado EPS/Afiliación",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )
    registro_civil_img = forms.FileField(
        label="Foto Registro Civil",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )
    otro_pais = forms.CharField(
        label="Especifique otro país",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Escriba el país de nacimiento...'})
    )
    tipo_sangre = forms.ChoiceField(
        choices=Nino.TIPO_SANGRE_CHOICES,
        label="Tipo de Sangre",
        required=False
    )
    parentesco = forms.ChoiceField(
        choices=Nino.PARENTESCO_CHOICES,
        label="Parentesco con el Niño",
        required=True
    )
    tiene_discapacidad = forms.BooleanField(
        label="¿Tiene alguna discapacidad?",
        required=False
    )
    tipos_discapacidad = forms.ModelMultipleChoiceField(
        queryset=Discapacidad.objects.all(),
        label="Tipo(s) de Discapacidad",
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    otra_discapacidad = forms.CharField(
        label="Otra discapacidad (especifique)",
        required=False
    )

    class Meta:
        model = Nino
        fields = [
            'nombres', 'apellidos', 'documento', 'fecha_nacimiento', 'genero', 'nacionalidad', 'otro_pais',
            'tipo_sangre', 'parentesco', 'tiene_discapacidad', 'tipos_discapacidad', 'otra_discapacidad',
            'foto', 'carnet_vacunacion', 'certificado_eps', 'registro_civil_img'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'nacionalidad': forms.Select(attrs={'class': 'nacionalidad-select'}),
        }
        labels = {
            'nacionalidad': '¿En qué país nació?',
        }

    def clean(self):
        cleaned_data = super().clean()
        tiene_discapacidad = cleaned_data.get('tiene_discapacidad')
        tipos_discapacidad = cleaned_data.get('tipos_discapacidad')
        otra_discapacidad = cleaned_data.get('otra_discapacidad')
        nacionalidad = cleaned_data.get('nacionalidad')
        otro_pais = cleaned_data.get('otro_pais')
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        
        # Validar edad del niño (debe estar entre 1 y 5 años)
        if fecha_nacimiento:
            from datetime import date
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            
            if edad < 1:
                self.add_error('fecha_nacimiento', 'El niño tiene menos de 1 año y no puede ser matriculado. La edad mínima es de 1 año.')
            elif edad > 5:
                self.add_error('fecha_nacimiento', 'El niño es mayor de 5 años y no puede ser matriculado. La edad máxima es de 5 años.')
        
        if tiene_discapacidad:
            if not tipos_discapacidad and not otra_discapacidad:
                self.add_error('tipos_discapacidad', 'Seleccione al menos un tipo de discapacidad o especifique otra.')
                
        # Validar que si selecciona "otro" país, debe especificarlo
        if nacionalidad == 'otro' and not otro_pais:
            self.add_error('otro_pais', 'Debe especificar el país cuando selecciona "Otro país".')
            
        return cleaned_data


# ----------------------------------------------------
# 👨 FORMULARIO DE REGISTRO DE PADRES (Expandido)
# ----------------------------------------------------
class PadreForm(forms.ModelForm):
    # Campos de Usuario
    documento = forms.IntegerField(label='Número de Documento', required=True)
    nombres = forms.CharField(max_length=50, label="Nombres", required=True)
    apellidos = forms.CharField(max_length=50, label="Apellidos", required=True)
    correo = forms.EmailField(label="Correo electrónico", required=True)
    tipo_documento = forms.ChoiceField(
        choices=[('CC', 'Cédula de ciudadanía'), ('TI', 'Tarjeta de identidad'), ('CE', 'Cédula de extranjería'), ('PA', 'Pasaporte')],
        label="Tipo de Documento",
        required=True
    )
    telefono = forms.CharField(max_length=20, label="Teléfono", required=True)
    
    # 🆕 Campos geográficos
    departamento_residencia = forms.ModelChoiceField(
        queryset=Departamento.objects.all().order_by('nombre'),
        required=True,
        label="Departamento de Residencia",
        empty_label="-- Seleccione un Departamento --"
    )
    ciudad_residencia = forms.ModelChoiceField(
        queryset=Municipio.objects.none(),
        required=True,
        label="Ciudad/Municipio",
        empty_label="-- Seleccione una Ciudad --"
    )
    localidad_bogota = forms.ModelChoiceField(
        queryset=LocalidadBogota.objects.all().order_by('numero'),
        required=False,
        label="Localidad (solo Bogotá)",
        empty_label="-- Seleccione una Localidad --"
    )
    
    direccion = forms.CharField(max_length=100, label="Dirección Completa", required=True)
    barrio = forms.CharField(max_length=100, label="Barrio", required=False)
    
    # Campos de Padre (perfil)
    OCUPACION_CHOICES = [
        ('', '-- Seleccione una ocupación --'),
        ('empleado_publico', 'Empleado Público'),
        ('empleado_privado', 'Empleado Privado'),
        ('independiente', 'Trabajador Independiente'),
        ('comerciante', 'Comerciante'),
        ('agricultor', 'Agricultor'),
        ('constructor', 'Constructor/Albañil'),
        ('conductor', 'Conductor'),
        ('docente', 'Docente/Educador'),
        ('salud', 'Profesional de la Salud'),
        ('servicios', 'Servicios (Limpieza, Seguridad, etc.)'),
        ('domestico', 'Trabajador Doméstico'),
        ('estudiante', 'Estudiante'),
        ('pensionado', 'Pensionado'),
        ('desempleado', 'Desempleado'),
        ('ama_casa', 'Ama de Casa'),
        ('vendedor', 'Vendedor'),
        ('mecanico', 'Mecánico'),
        ('artesano', 'Artesano'),
        ('otro', 'Otro')
    ]
    
    ocupacion = forms.ChoiceField(
        choices=OCUPACION_CHOICES,
        label="Ocupación",
        required=True,
        widget=forms.Select(attrs={'class': 'ocupacion-select'})
    )
    otra_ocupacion = forms.CharField(
        max_length=50, 
        required=False, 
        label="Especifique otra ocupación",
        widget=forms.TextInput(attrs={'placeholder': 'Escriba la ocupación...'})
    )
    estrato = forms.IntegerField(
        label="Estrato",
        required=False,
        min_value=1,
        max_value=6,
        widget=forms.NumberInput(attrs={'min': '1', 'max': '6'})
    )
    telefono_contacto_emergencia = forms.CharField(
        max_length=20,
        label="Teléfono de Contacto de Emergencia",
        required=False
    )
    nombre_contacto_emergencia = forms.CharField(
        max_length=100,
        label="Nombre del Contacto de Emergencia",
        required=False
    )
    situacion_economica_hogar = forms.CharField(
        max_length=100,
        label="Situación Económica del Hogar",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )
    documento_identidad_img = forms.FileField(
        label="Cédula/Documento de Identidad",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )
    clasificacion_sisben = forms.FileField(
        label="Foto Clasificación SISBEN",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )

    class Meta:
        model = Usuario
        fields = ['tipo_documento', 'documento', 'nombres', 'apellidos', 'correo', 'telefono',
                  'departamento_residencia', 'ciudad_residencia', 'localidad_bogota', 'direccion', 'barrio']
        widgets = {
            'telefono': forms.TextInput(attrs={'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar municipios si hay departamento seleccionado
        if 'departamento_residencia' in self.data:
            try:
                departamento_id = int(self.data.get('departamento_residencia'))
                self.fields['ciudad_residencia'].queryset = Municipio.objects.filter(
                    departamento_id=departamento_id
                ).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['ciudad_residencia'].queryset = Municipio.objects.none()
        elif self.instance.pk and self.instance.departamento_residencia:
            self.fields['ciudad_residencia'].queryset = Municipio.objects.filter(
                departamento=self.instance.departamento_residencia
            ).order_by('nombre')

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
        ocupacion = cleaned_data.get('ocupacion')
        otra_ocupacion = cleaned_data.get('otra_ocupacion')
        
        if not documento or not str(documento).isdigit():
            self.add_error('documento', 'El documento debe ser un número válido.')
            
        # Validar que si selecciona "otro", debe especificar la ocupación
        if ocupacion == 'otro' and not otra_ocupacion:
            self.add_error('otra_ocupacion', 'Debe especificar la ocupación cuando selecciona "Otro".')
            
        return cleaned_data


# ----------------------------------------------------
# 🆕 NUEVOS FORMULARIOS PARA MEJORAS DE MATRÍCULA
# ----------------------------------------------------

class NinoSoloForm(forms.ModelForm):
    """Formulario solo para el niño cuando se asigna a un padre existente"""
    foto = forms.ImageField(
        label="Foto del Niño",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    carnet_vacunacion = forms.FileField(
        label="Carné de Vacunación",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )
    certificado_eps = forms.FileField(
        label="Certificado EPS/Afiliación",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )
    registro_civil_img = forms.FileField(
        label="Foto Registro Civil",
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )
    otro_pais = forms.CharField(
        label="Especifique otro país",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Escriba el país de nacimiento...'})
    )
    tipo_sangre = forms.ChoiceField(
        choices=Nino.TIPO_SANGRE_CHOICES,
        label="Tipo de Sangre",
        required=False
    )
    parentesco = forms.ChoiceField(
        choices=Nino.PARENTESCO_CHOICES,
        label="Parentesco con el Niño",
        required=True
    )
    tiene_discapacidad = forms.BooleanField(
        label="¿Tiene alguna discapacidad?",
        required=False
    )
    tipos_discapacidad = forms.ModelMultipleChoiceField(
        queryset=Discapacidad.objects.all(),
        label="Tipo(s) de Discapacidad",
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    otra_discapacidad = forms.CharField(
        label="Otra discapacidad (especifique)",
        required=False
    )

    class Meta:
        model = Nino
        fields = [
            'nombres', 'apellidos', 'documento', 'fecha_nacimiento', 'genero', 'nacionalidad', 'otro_pais',
            'tipo_sangre', 'parentesco', 'tiene_discapacidad', 'tipos_discapacidad', 'otra_discapacidad',
            'foto', 'carnet_vacunacion', 'certificado_eps', 'registro_civil_img'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'nacionalidad': forms.Select(attrs={'class': 'nacionalidad-select'}),
        }
        labels = {
            'nacionalidad': '¿En qué país nació?',
        }

    def clean(self):
        cleaned_data = super().clean()
        tiene_discapacidad = cleaned_data.get('tiene_discapacidad')
        tipos_discapacidad = cleaned_data.get('tipos_discapacidad')
        otra_discapacidad = cleaned_data.get('otra_discapacidad')
        nacionalidad = cleaned_data.get('nacionalidad')
        otro_pais = cleaned_data.get('otro_pais')
        
        if tiene_discapacidad:
            if not tipos_discapacidad and not otra_discapacidad:
                self.add_error('tipos_discapacidad', 'Seleccione al menos un tipo de discapacidad o especifique otra.')
                
        # Validar que si selecciona "otro" país, debe especificarlo
        if nacionalidad == 'otro' and not otro_pais:
            self.add_error('otro_pais', 'Debe especificar el país cuando selecciona "Otro país".')
            
        return cleaned_data


class BuscarPadreForm(forms.Form):
    """Formulario para buscar un padre por documento"""
    documento = forms.CharField(
        label="Documento del Padre",
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese el documento del padre...',
            'class': 'buscar-padre-documento'
        })
    )
    
    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if not documento or not documento.isdigit():
            raise forms.ValidationError('El documento debe ser un número válido.')
        return documento


class CambiarPadreForm(forms.Form):
    """Formulario para seleccionar niño y cambiar su padre"""
    nino = forms.ModelChoiceField(
        queryset=Nino.objects.none(),  # Se configurará dinámicamente
        label="Seleccionar Niño",
        empty_label="-- Seleccione el niño --",
        widget=forms.Select(attrs={'class': 'nino-select'})
    )
    
    def __init__(self, hogar=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hogar:
            self.fields['nino'].queryset = Nino.objects.filter(hogar=hogar).order_by('nombres', 'apellidos')


# ========================================================================================
# 🏠 FORMULARIOS PARA SISTEMA DE VISITAS TÉCNICAS
# ========================================================================================

class AgendarVisitaTecnicaForm(forms.ModelForm):
    """
    Formulario para agendar una visita técnica a un hogar comunitario.
    """
    class Meta:
        model = VisitaTecnica
        fields = [
            'hogar', 'fecha_programada', 'visitador', 'tipo_visita', 
            'observaciones_agenda'
        ]
        widgets = {
            'fecha_programada': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'hogar': forms.Select(attrs={'class': 'form-control'}),
            'visitador': forms.Select(attrs={'class': 'form-control'}),
            'tipo_visita': forms.Select(attrs={'class': 'form-control'}),
            'observaciones_agenda': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones o instrucciones especiales para la visita...'
            }),
        }
        labels = {
            'hogar': 'Hogar Comunitario',
            'fecha_programada': 'Fecha y Hora de la Visita',
            'visitador': 'Visitador Asignado',
            'tipo_visita': 'Tipo de Visita',
            'observaciones_agenda': 'Observaciones'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo hogares pendientes de visita
        self.fields['hogar'].queryset = HogarComunitario.objects.filter(
            estado__in=['pendiente_visita', 'visita_agendada']
        ).select_related('madre__usuario')
        
        # Filtrar solo usuarios administradores para visitadores
        self.fields['visitador'].queryset = Usuario.objects.filter(
            rol__nombre_rol='administrador'
        )


class ActaVisitaTecnicaForm(forms.ModelForm):
    """
    Formulario completo para el Acta de Visita Técnica (V1).
    Dividido en secciones según los requisitos.
    """
    class Meta:
        model = ActaVisitaTecnica
        exclude = ['visita', 'fecha_creacion', 'fecha_actualizacion', 'completado_por', 
                   'area_social_total', 'patio_total', 'capacidad_calculada']
        
        widgets = {
            # A. Geolocalización
            'geolocalizacion_lat_verificada': forms.NumberInput(attrs={
                'step': '0.0000001',
                'placeholder': '4.6097100',
                'class': 'form-control'
            }),
            'geolocalizacion_lon_verificada': forms.NumberInput(attrs={
                'step': '0.0000001',
                'placeholder': '-74.0817500',
                'class': 'form-control'
            }),
            'direccion_verificada': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección verificada in situ'
            }),
            'direccion_coincide': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones_direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'estrato_verificado': forms.NumberInput(attrs={
                'min': 1,
                'max': 6,
                'class': 'form-control'
            }),
            'estrato_coincide': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'foto_recibo_servicio': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            
            # B. Servicios
            'tiene_agua_potable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'agua_continua': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'agua_legal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tiene_energia': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'energia_continua': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'energia_legal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tiene_alcantarillado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'manejo_excretas_adecuado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            # Infraestructura
            'estado_pisos': forms.Select(attrs={'class': 'form-control'}),
            'estado_paredes': forms.Select(attrs={'class': 'form-control'}),
            'estado_techos': forms.Select(attrs={'class': 'form-control'}),
            'ventilacion_adecuada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'iluminacion_natural_adecuada': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones_infraestructura': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # Riesgos
            'proximidad_rios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'proximidad_deslizamientos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'proximidad_trafico_intenso': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'proximidad_contaminacion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'nivel_riesgo_general': forms.Select(attrs={'class': 'form-control'}),
            'descripcion_riesgos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # C. Espacios
            'area_social_largo': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'metros',
                'class': 'form-control'
            }),
            'area_social_ancho': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'metros',
                'class': 'form-control'
            }),
            'foto_area_social_medidas': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            
            'tiene_patio_cubierto': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'patio_largo': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'metros',
                'class': 'form-control'
            }),
            'patio_ancho': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'metros',
                'class': 'form-control'
            }),
            'foto_patio_medidas': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            
            # Baños
            'num_banos_verificado': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control'
            }),
            'estado_higiene_banos': forms.Select(attrs={'class': 'form-control'}),
            'foto_bano_1': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            'foto_bano_2': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            
            # Fachada
            'foto_fachada': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            'foto_fachada_numeracion': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            
            # D. Capacidad
            'capacidad_recomendada': forms.NumberInput(attrs={
                'min': 1,
                'max': 30,
                'class': 'form-control'
            }),
            'justificacion_capacidad': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # E. Resultado
            'resultado_visita': forms.Select(attrs={'class': 'form-control'}),
            'observaciones_generales': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'recomendaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'condiciones_aprobacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # Firmas
            'firma_visitador': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            'firma_madre': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que si tiene patio, tenga medidas
        tiene_patio = cleaned_data.get('tiene_patio_cubierto')
        if tiene_patio:
            if not cleaned_data.get('patio_largo') or not cleaned_data.get('patio_ancho'):
                raise forms.ValidationError(
                    'Si tiene patio cubierto, debe proporcionar las medidas (largo y ancho)'
                )
        
        # Validar que si es aprobado con condiciones, tenga condiciones especificadas
        resultado = cleaned_data.get('resultado_visita')
        if resultado == 'aprobado_condiciones' and not cleaned_data.get('condiciones_aprobacion'):
            raise forms.ValidationError(
                'Si el resultado es "Aprobado con Condiciones", debe especificar las condiciones'
            )
        
        return cleaned_data


# ============================================================================
# 🆕 NUEVOS FORMULARIOS - SISTEMA DE DOS FASES
# ============================================================================

# ----------------------------------------------------
# 📝 FORMULARIO 1: Registro Inicial del Hogar
# ----------------------------------------------------
class HogarFormulario1Form(forms.ModelForm):
    """
    Formulario para el registro inicial del hogar comunitario.
    Solo incluye campos básicos para crear el registro y programar la visita técnica.
    
    Campos incluidos:
    - Ubicación: Regional, Ciudad, Localidad (Bogotá), Dirección, Barrio
    - Identificación: Nombre del hogar
    - Visita: Fecha programada para la primera visita técnica
    - Estado: Siempre "pendiente_revision"
    """
    
    regional = forms.ModelChoiceField(
        queryset=Regional.objects.all().order_by('nombre'),
        required=True,
        label="Regional",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Seleccione una Regional --"
    )
    ciudad = forms.ModelChoiceField(
        queryset=Ciudad.objects.none(),
        required=True,
        label="Ciudad",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Seleccione una Ciudad --"
    )
    localidad_bogota = forms.ModelChoiceField(
        queryset=LocalidadBogota.objects.all().order_by('nombre'),
        required=False,
        label="Localidad (solo para Bogotá)",
        widget=forms.Select(attrs={'id': 'id_localidad_hogar', 'class': 'form-control'}),
        empty_label="-- Seleccione una Localidad --"
    )
    
    class Meta:
        model = HogarComunitario
        fields = [
            'regional', 'ciudad', 'localidad_bogota', 'direccion', 'barrio',
            'nombre_hogar', 'fecha_primera_visita'
        ]
        labels = {
            'nombre_hogar': 'Nombre del Hogar Comunitario',
            'direccion': 'Dirección Completa',
            'barrio': 'Barrio',
            'fecha_primera_visita': 'Fecha Programada para Primera Visita Técnica',
        }
        widgets = {
            'nombre_hogar': forms.TextInput(attrs={
                'placeholder': 'Ej: Hogar Comunitario Los Ángeles',
                'class': 'form-control'
            }),
            'direccion': forms.TextInput(attrs={
                'placeholder': 'Ej: Cra 97#135a-30 SUBA',
                'id': 'id_direccion_hogar',
                'class': 'form-control'
            }),
            'barrio': forms.TextInput(attrs={
                'placeholder': 'Ej: El Poblado, Chapinero, etc.',
                'class': 'form-control'
            }),
            'fecha_primera_visita': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': '2025-01-01'  # No permitir fechas pasadas
            }),
        }
        help_texts = {
            'nombre_hogar': 'Nombre con el cual será identificado el hogar comunitario',
            'direccion': 'Dirección completa del hogar (será verificada con la localidad)',
            'fecha_primera_visita': 'Fecha en la cual se realizará la visita técnica de verificación',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar ciudades si hay regional seleccionada
        if 'regional' in self.data:
            try:
                regional_id = int(self.data.get('regional'))
                self.fields['ciudad'].queryset = Ciudad.objects.filter(
                    regional_id=regional_id
                ).order_by('nombre')
            except (ValueError, TypeError):
                self.fields['ciudad'].queryset = Ciudad.objects.none()
        elif self.instance and self.instance.pk and self.instance.regional:
            self.fields['ciudad'].queryset = Ciudad.objects.filter(
                regional=self.instance.regional
            ).order_by('nombre')
        else:
            self.fields['ciudad'].queryset = Ciudad.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        ciudad = cleaned_data.get('ciudad')
        localidad_bogota = cleaned_data.get('localidad_bogota')
        
        # Si la ciudad es Bogotá, validar que se seleccione una localidad
        if ciudad and ciudad.nombre.upper() == 'BOGOTÁ':
            if not localidad_bogota:
                self.add_error(
                    'localidad_bogota',
                    'Debe seleccionar una localidad para hogares en Bogotá'
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Establecer estado inicial
        instance.estado = 'pendiente_revision'
        instance.formulario_completo = False  # Marca que falta el formulario 2
        
        if commit:
            instance.save()
        return instance


# ----------------------------------------------------
# 👥 FORMULARIO: Convivientes del Hogar
# ----------------------------------------------------
from django.forms import BaseInlineFormSet

class ConvivienteFormSet(BaseInlineFormSet):
    """
    FormSet para los convivientes del hogar.
    Permite agregar múltiples personas que viven en el hogar.
    """
    
    def clean(self):
        """Validar que no haya documentos duplicados entre convivientes"""
        if any(self.errors):
            return
        
        documentos = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                documento = form.cleaned_data.get('numero_documento')
                if documento:
                    if documento in documentos:
                        raise forms.ValidationError(
                            f'El documento {documento} está duplicado. '
                            'Cada conviviente debe tener un documento único.'
                        )
                    documentos.append(documento)


class ConvivienteForm(forms.ModelForm):
    """
    Formulario individual para cada conviviente del hogar.
    Incluye información básica y documento de antecedentes.
    """
    
    class Meta:
        model = ConvivienteHogar
        fields = [
            'tipo_documento', 'numero_documento', 'nombre_completo',
            'parentesco', 'antecedentes_pdf'
        ]
        labels = {
            'tipo_documento': 'Tipo de Documento',
            'numero_documento': 'Número de Documento',
            'nombre_completo': 'Nombre Completo',
            'parentesco': 'Parentesco con el Agente Educativo',
            'antecedentes_pdf': 'Certificado de Antecedentes (PDF)',
        }
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1234567890'
            }),
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del conviviente'
            }),
            'parentesco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Esposo(a), Hijo(a), Padre/Madre, etc.'
            }),
            'antecedentes_pdf': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': 'form-control'
            }),
        }
        help_texts = {
            'antecedentes_pdf': 'Certificado de antecedentes judiciales y disciplinarios (obligatorio)',
            'numero_documento': 'Sin puntos ni espacios',
        }
    
    def clean_numero_documento(self):
        """Validar formato del documento"""
        documento = self.cleaned_data.get('numero_documento', '').strip()
        if not documento:
            raise forms.ValidationError('El número de documento es obligatorio')
        
        # Remover espacios y puntos
        documento = documento.replace(' ', '').replace('.', '').replace(',', '')
        
        return documento


# ----------------------------------------------------
# 📋 FORMULARIO 2: Visita Técnica y Validación
# ----------------------------------------------------
class HogarFormulario2Form(forms.ModelForm):
    """
    Formulario para la visita técnica del hogar comunitario.
    Se completa después de realizar la visita física al inmueble.
    
    Incluye:
    - Características físicas del inmueble
    - Área social en m² (OBLIGATORIO ≥24m²)
    - Capacidad calculada automáticamente
    - Fotos del interior y exterior
    - Documentos de tenencia
    - Geolocalización
    """
    
    class Meta:
        model = HogarComunitario
        fields = [
            'estrato', 'num_habitaciones', 'num_banos', 'material_construccion',
            'riesgos_cercanos', 'area_social_m2', 'fotos_interior', 'fotos_exterior',
            'geolocalizacion_lat', 'geolocalizacion_lon', 'tipo_tenencia',
            'documento_tenencia_pdf'
        ]
        labels = {
            'estrato': 'Estrato Socioeconómico',
            'num_habitaciones': 'Número de Habitaciones',
            'num_banos': 'Número de Baños',
            'material_construccion': 'Material de Construcción',
            'riesgos_cercanos': 'Riesgos Cercanos al Hogar',
            'area_social_m2': 'Área Social del Hogar (m²)',
            'fotos_interior': 'Fotos del Interior (mínimo 3)',
            'fotos_exterior': 'Fotos del Exterior (mínimo 1)',
            'geolocalizacion_lat': 'Latitud',
            'geolocalizacion_lon': 'Longitud',
            'tipo_tenencia': 'Tipo de Tenencia del Inmueble',
            'documento_tenencia_pdf': 'Documento de Tenencia (PDF)',
        }
        widgets = {
            'estrato': forms.NumberInput(attrs={
                'min': 1,
                'max': 6,
                'class': 'form-control'
            }),
            'num_habitaciones': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control'
            }),
            'num_banos': forms.NumberInput(attrs={
                'min': 1,
                'class': 'form-control'
            }),
            'material_construccion': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Ej: Ladrillo, concreto, madera, etc.',
                'class': 'form-control'
            }),
            'riesgos_cercanos': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ej: Cerca de vías principales, zona de inundación, etc.',
                'class': 'form-control'
            }),
            'area_social_m2': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '24.00',
                'placeholder': 'Ej: 30.50',
                'class': 'form-control'
            }),
            'fotos_interior': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            'fotos_exterior': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            'geolocalizacion_lat': forms.NumberInput(attrs={
                'step': '0.0000001',
                'placeholder': 'Ej: 4.6097100',
                'class': 'form-control'
            }),
            'geolocalizacion_lon': forms.NumberInput(attrs={
                'step': '0.0000001',
                'placeholder': 'Ej: -74.0817500',
                'class': 'form-control'
            }),
            'tipo_tenencia': forms.Select(attrs={'class': 'form-control'}),
            'documento_tenencia_pdf': forms.FileInput(attrs={
                'accept': 'application/pdf',
                'class': 'form-control'
            }),
        }
        help_texts = {
            'area_social_m2': '⚠️ OBLIGATORIO: Mínimo 24 m². La capacidad se calcula como: piso(m²/2)',
            'fotos_interior': 'Subir mínimo 3 fotos (sala, baño, habitación)',
            'fotos_exterior': 'Subir mínimo 1 foto de la fachada o entrada',
            'geolocalizacion_lat': 'Coordenada de latitud (use Google Maps para obtenerla)',
            'geolocalizacion_lon': 'Coordenada de longitud (use Google Maps para obtenerla)',
            'tipo_tenencia': 'Indique si el inmueble es propio, arrendado o en comodato',
            'documento_tenencia_pdf': 'Documento que acredite la tenencia del inmueble',
        }
    
    def clean_area_social_m2(self):
        """Validar que el área cumpla con el mínimo requerido"""
        area = self.cleaned_data.get('area_social_m2')
        
        if area is None:
            raise forms.ValidationError(
                '⚠️ El área social es OBLIGATORIA para aprobar el hogar.'
            )
        
        if area < 24:
            raise forms.ValidationError(
                f'⚠️ El área social debe ser de al menos 24 m². '
                f'El área ingresada ({area} m²) NO CUMPLE con los requisitos mínimos. '
                f'El hogar NO PUEDE SER APROBADO con esta área.'
            )
        
        return area
    
    def clean(self):
        cleaned_data = super().clean()
        area = cleaned_data.get('area_social_m2')
        
        # Calcular capacidad automáticamente si hay área
        if area:
            import math
            capacidad = math.floor(area / 2)
            
            # Limitar a máximo 15 niños según normativa
            if capacidad > 15:
                capacidad = 15
            
            cleaned_data['capacidad_calculada'] = capacidad
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Calcular y guardar la capacidad
        if instance.area_social_m2:
            import math
            capacidad = math.floor(instance.area_social_m2 / 2)
            instance.capacidad_calculada = min(capacidad, 15)  # Máximo 15
            instance.capacidad_maxima = instance.capacidad_calculada
        
        # Marcar formulario como completo
        instance.formulario_completo = True
        
        # Cambiar estado a "en_revision" para que el administrador revise
        instance.estado = 'en_revision'
        
        if commit:
            instance.save()
        return instance