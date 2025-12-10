from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# ------------------------
# Discapacidad
# ------------------------
class Discapacidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'discapacidades'
        verbose_name = 'Discapacidad'
        verbose_name_plural = 'Discapacidades'

    def __str__(self):
        return self.nombre
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator

# ------------------------
# Roles del sistema
# ------------------------
class Rol(models.Model):
    nombre_rol = models.CharField(
        max_length=30,
        choices=[
            ('administrador', 'administrador'),
            ('madre_comunitaria', 'madre_comunitaria'),
            ('padre', 'padre'),
        ],
        unique=True
    )

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.nombre_rol

# ------------------------
# 💡 NUEVO: Regionales
# ------------------------
class Regional(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'regionales'
        verbose_name = 'Regional'
        verbose_name_plural = 'Regionales'

    def __str__(self):
        return self.nombre

def madre_upload_path(instance, filename):
    return f"madres_documentos/{instance.usuario.documento}/{filename}"
def admin_upload_path(instance, filename):
    # Guarda la foto en una carpeta por documento, igual que madres
    return f"administradores/fotos/{instance.documento}/{filename}"
# ------------------------
# Ciudades (para Hogares Comunitarios - relación con Regional)
# ------------------------
class Ciudad(models.Model):
    nombre = models.CharField(max_length=120)
    regional = models.ForeignKey(Regional, on_delete=models.CASCADE, related_name="ciudades")

    def __str__(self):
        return self.nombre

# ------------------------
# 🆕 GEOGRAFÍA DE COLOMBIA
# ------------------------
class Departamento(models.Model):
    """Departamentos de Colombia (32 + Bogotá D.C.)"""
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, unique=True, null=True, blank=True)  # Código DANE
    
    class Meta:
        db_table = 'departamentos'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Municipio(models.Model):
    """Municipios (ciudades y pueblos) de Colombia por departamento"""
    nombre = models.CharField(max_length=150)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='municipios')
    codigo = models.CharField(max_length=10, null=True, blank=True)  # Código DANE
    es_capital = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'municipios'
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['departamento__nombre', 'nombre']
        unique_together = ['nombre', 'departamento']
    
    def __str__(self):
        return f"{self.nombre} ({self.departamento.nombre})"

class LocalidadBogota(models.Model):
    """20 Localidades de Bogotá D.C."""
    nombre = models.CharField(max_length=100, unique=True)
    numero = models.IntegerField(unique=True)  # 1-20
    
    class Meta:
        db_table = 'localidades_bogota'
        verbose_name = 'Localidad de Bogotá'
        verbose_name_plural = 'Localidades de Bogotá'
        ordering = ['numero']
    
    def __str__(self):
        return f"{self.numero}. {self.nombre}"

# ------------------------
# Gestor de usuarios personalizado
# ------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, documento, password=None, **extra_fields):
        if not documento:
            raise ValueError('El campo Documento es obligatorio.')

        user = self.model(documento=documento, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, documento, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        rol_admin, _ = Rol.objects.get_or_create(nombre_rol='administrador')
        extra_fields['rol'] = rol_admin
        return self.create_user(documento, password, **extra_fields)



# ------------------------
# Usuario personalizado
# ------------------------
class Usuario(AbstractUser):
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de ciudadanía'),
        ('TI', 'Tarjeta de identidad'),
        ('CE', 'Cédula de extranjería'),
        ('PA', 'Pasaporte'),
    ]
    
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    username = None

    tipo_documento = models.CharField(max_length=5, choices=TIPO_DOCUMENTO_CHOICES, default='CC')
    documento = models.BigIntegerField(unique=True)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    correo = models.EmailField(max_length=100, unique=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='F')
    
    # 🆕 Ubicación geográfica
    departamento_residencia = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='residentes')
    ciudad_residencia = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True, related_name='residentes')
    localidad_bogota = models.ForeignKey(LocalidadBogota, on_delete=models.SET_NULL, null=True, blank=True, related_name='residentes', 
                                         help_text='Solo aplica si vive en Bogotá D.C.')
    
    direccion = models.CharField(max_length=100, null=True, blank=True)
    barrio = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    nivel_educativo = models.CharField(max_length=50, null=True, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True)
    # Foto de perfil para administradores (y opcional para cualquier usuario)
    foto_admin = models.ImageField(upload_to=admin_upload_path, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
   
    # 💡 CORRECCIÓN CLAVE: Indicarle a Django cuál es el campo de email.
    # Esto es fundamental para que funciones como "olvidé mi contraseña" funcionen
    # sin necesidad de código extra complejo.
    EMAIL_FIELD = 'correo'

    USERNAME_FIELD = 'documento'
    REQUIRED_FIELDS = ['nombres', 'apellidos', 'correo', 'tipo_documento']

    objects = CustomUserManager()

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.documento})"
 
# ------------------------
# Padre o Tutor
# ------------------------
class Padre(models.Model):
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

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='padre_profile')
    ocupacion = models.CharField(max_length=50, choices=OCUPACION_CHOICES, null=True, blank=True)
    otra_ocupacion = models.CharField(max_length=50, null=True, blank=True)
    estrato = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(6)])

    telefono_contacto_emergencia = models.CharField(max_length=20, null=True, blank=True)
    nombre_contacto_emergencia = models.CharField(max_length=100, null=True, blank=True)
    situacion_economica_hogar = models.CharField(max_length=100, null=True, blank=True)
    documento_identidad_img = models.FileField(max_length=255, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    clasificacion_sisben = models.FileField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'padres'

    def __str__(self):
        return f"Padre: {self.usuario.nombres} {self.usuario.apellidos}"

#-------------------------------
#CAMPOS NUEVOS PARA MADRES COMUNITARIAS
# ------------------------
# Madre Comunitaria
# ------------------------
class MadreComunitaria(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='madre_profile')
    NIVEL_ESCOLARIDAD_CHOICES = [
        ('Primaria', 'Primaria'),
        ('Bachiller', 'Bachiller'),
        ('Técnico', 'Técnico'),
        ('Tecnólogo', 'Tecnólogo'),
        ('Profesional', 'Profesional')
    ]
    # Información académica y experiencia
    nivel_escolaridad = models.CharField(max_length=100, choices=NIVEL_ESCOLARIDAD_CHOICES)
    titulo_obtenido = models.CharField(max_length=150, null=True, blank=True)
    institucion = models.CharField(max_length=150, null=True, blank=True)
    experiencia_previa = models.TextField(null=True, blank=True)
    certificado_laboral = models.FileField(upload_to='madres_documentos/certificados_laborales/', null=True, blank=True)

    # Declaraciones
    no_retirado_icbf = models.BooleanField(default=False)
    carta_disponibilidad = models.FileField(upload_to='madres_documentos/disponibilidad/', null=True, blank=True)
    firma_digital = models.FileField(upload_to='madres_documentos/firmas/', null=True, blank=True)

    foto_madre = models.ImageField(upload_to='madres_documentos/fotos/', null=True, blank=True)
    # Documentos soporte
    documento_identidad_pdf = models.FileField(upload_to='madres_documentos/cedulas/', null=True, blank=True)
    certificado_escolaridad_pdf = models.FileField(upload_to='madres_documentos/educacion/', null=True, blank=True)
    certificado_antecedentes_pdf = models.FileField(upload_to='madres_documentos/antecedentes/', null=True, blank=True)
    certificado_medico_pdf = models.FileField(upload_to='madres_documentos/medico/', null=True, blank=True)
    certificado_residencia_pdf = models.FileField(upload_to='madres_documentos/residencia/', null=True, blank=True)
    cartas_recomendacion_pdf = models.FileField(upload_to='madres_documentos/recomendaciones/', null=True, blank=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'madres_comunitarias'

    def __str__(self):
        return f"Madre Comunitaria: {self.usuario.nombres} {self.usuario.apellidos}"




# ------------------------
# Hogares Comunitarios
# ------------------------
# ------------------------
# Hogares Comunitarios (actualizado)
# ------------------------
class HogarComunitario(models.Model):
    # 💡 NUEVO: Relación con la regional. Es obligatorio para cada hogar.
    # Usamos PROTECT para evitar que se borre una regional si tiene hogares asociados.
    regional = models.ForeignKey(Regional, on_delete=models.PROTECT, related_name='hogares')
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT, related_name='hogares')
    nombre_hogar = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    localidad = models.CharField(max_length=100, blank=True, default='')  # Mantener para hogares antiguos, se asigna en la vista
    localidad_bogota = models.ForeignKey('LocalidadBogota', on_delete=models.SET_NULL, null=True, blank=True, related_name='hogares')
    barrio = models.CharField(max_length=100, null=True, blank=True)
    estrato = models.IntegerField(null=True, blank=True)

    # 🆕 NUEVOS CAMPOS - FORMULARIO 1
    fecha_primera_visita = models.DateField(null=True, blank=True, help_text="Fecha programada para la primera visita técnica")
    
    # 🆕 SISTEMA DE VISITAS Y ESTADO DE APTITUD
    ultima_visita = models.DateField(null=True, blank=True, help_text="Fecha de la última visita técnica realizada")
    proxima_visita = models.DateField(null=True, blank=True, help_text="Fecha programada para la próxima visita técnica (calculada automáticamente)")
    observaciones_visita = models.TextField(blank=True, help_text="Observaciones de la última visita técnica realizada")
    estado_aptitud = models.CharField(
        max_length=20,
        choices=[
            ('no_apto', 'No Apto'),
            ('apto', 'Apto'),
        ],
        default='no_apto',
        help_text="Estado de aptitud del hogar. Se actualiza a 'Apto' después de la primera visita aprobada"
    )
    
    # 🆕 NUEVOS CAMPOS - FORMULARIO 2 (Visita Técnica)
    area_social_m2 = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, 
                                         help_text="Metros cuadrados del área social disponible para los niños")
    capacidad_calculada = models.IntegerField(null=True, blank=True, 
                                              help_text="Capacidad calculada según área social (m²/2)")
    formulario_completo = models.BooleanField(default=False, 
                                              help_text="Indica si se completó el formulario 2 de visita técnica")
    
    # Infraestructura (FORMULARIO 2)
    num_habitaciones = models.IntegerField(null=True, blank=True)
    num_banos = models.IntegerField(null=True, blank=True)
    material_construccion = models.TextField(null=True, blank=True)
    riesgos_cercanos = models.TextField(null=True, blank=True)

    # Fotos y geolocalización (FORMULARIO 2)
    fotos_interior = models.FileField(upload_to='hogares/fotos_interior/', null=True, blank=True)
    fotos_exterior = models.FileField(upload_to='hogares/fotos_exterior/', null=True, blank=True)
    geolocalizacion_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    geolocalizacion_lon = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Tenencia del inmueble (FORMULARIO 2)
    tipo_tenencia = models.CharField(max_length=50, choices=[
        ('Propia', 'Propia'),
        ('Arrendada', 'Arrendada'),
        ('Comodato', 'Comodato')
    ], null=True, blank=True)
    documento_tenencia_pdf = models.FileField(upload_to='hogares/documentos_tenencia/', null=True, blank=True)

    # Estado y relación
    capacidad_maxima = models.IntegerField(default=15, help_text="Capacidad máxima aprobada después de visita técnica")
    estado = models.CharField(
        max_length=30,
        choices=[
            ('pendiente_revision', 'Pendiente de Revisión'),
            ('en_revision', 'En Revisión'),
            ('aprobado', 'Aprobado'),
            ('rechazado', 'Rechazado'),
            ('en_mantenimiento', 'En Mantenimiento'),
            # Legacy states (mantener por compatibilidad)
            ('pendiente_visita', 'Pendiente de Visita'),
            ('visita_agendada', 'Visita Agendada'),
            ('en_evaluacion', 'En Evaluación'),
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
        ],
        default='pendiente_revision'
    )
    madre = models.ForeignKey(MadreComunitaria, on_delete=models.PROTECT, related_name='hogares_asignados')

    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_habilitacion = models.DateTimeField(null=True, blank=True)  # Cuando pasa a activo/aprobado

    class Meta:
        db_table = 'hogares_comunitarios'

    def __str__(self):
        return self.nombre_hogar
# ------------------------
# Convivientes del Hogar Comunitario
# ------------------------
class ConvivienteHogar(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
        ('RC', 'Registro Civil'),
    ]
    
    hogar = models.ForeignKey(HogarComunitario, on_delete=models.CASCADE, related_name='convivientes')
    tipo_documento = models.CharField(max_length=2, choices=TIPO_DOCUMENTO_CHOICES, default='CC')
    numero_documento = models.CharField(max_length=20)
    nombre_completo = models.CharField(max_length=200)
    parentesco = models.CharField(max_length=50)
    antecedentes_pdf = models.FileField(upload_to='hogares/antecedentes_convivientes/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # Campos legacy (mantener por compatibilidad)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    cedula = models.BigIntegerField(null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'convivientes_hogar'

    def __str__(self):
        return f"{self.nombre_completo} ({self.parentesco}) - Hogar: {self.hogar.nombre_hogar}"


# ------------------------
# Niños
# ------------------------
class Nino(models.Model):
    TIPO_SANGRE_CHOICES = [
        ('O+', 'O+'), ('O-', 'O-'), ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]
    PARENTESCO_CHOICES = [
        ('padre', 'Padre'), ('madre', 'Madre'), ('tutor', 'Tutor'),
        ('abuelo', 'Abuelo/a'), ('tio', 'Tío/a'), ('hermano', 'Hermano/a'),
        ('otro', 'Otro')
    ]

    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    documento = models.BigIntegerField(null=True, blank=True)
    genero = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ('masculino', 'masculino'),
            ('femenino', 'femenino'),
            ('otro', 'otro'),
            ('no_especificado', 'no_especificado')
        ]
    )
    tipo_sangre = models.CharField(max_length=3, choices=TIPO_SANGRE_CHOICES, null=True, blank=True)
    parentesco = models.CharField(max_length=20, choices=PARENTESCO_CHOICES, null=True, blank=True)
    tiene_discapacidad = models.BooleanField(default=False)
    tipos_discapacidad = models.ManyToManyField('Discapacidad', blank=True)
    otra_discapacidad = models.CharField(max_length=100, null=True, blank=True)
    
    PAIS_NACIMIENTO_CHOICES = [
        ('', '-- Seleccione el país de nacimiento --'),
        ('colombia', 'Colombia'),
        ('venezuela', 'Venezuela'),
        ('ecuador', 'Ecuador'),
        ('peru', 'Perú'),
        ('panama', 'Panamá'),
        ('brasil', 'Brasil'),
        ('argentina', 'Argentina'),
        ('chile', 'Chile'),
        ('bolivia', 'Bolivia'),
        ('paraguay', 'Paraguay'),
        ('uruguay', 'Uruguay'),
        ('mexico', 'México'),
        ('costa_rica', 'Costa Rica'),
        ('nicaragua', 'Nicaragua'),
        ('honduras', 'Honduras'),
        ('guatemala', 'Guatemala'),
        ('el_salvador', 'El Salvador'),
        ('cuba', 'Cuba'),
        ('republica_dominicana', 'República Dominicana'),
        ('haiti', 'Haití'),
        ('estados_unidos', 'Estados Unidos'),
        ('canada', 'Canadá'),
        ('espana', 'España'),
        ('italia', 'Italia'),
        ('francia', 'Francia'),
        ('alemania', 'Alemania'),
        ('otro', 'Otro país')
    ]
    
    nacionalidad = models.CharField(
        max_length=50, 
        choices=PAIS_NACIMIENTO_CHOICES,
        null=True, 
        blank=True,
        verbose_name="País de nacimiento"
    )
    otro_pais = models.CharField(max_length=50, null=True, blank=True, verbose_name="Otro país (especifique)")
    fecha_ingreso = models.DateField(auto_now_add=True, verbose_name="Fecha de ingreso al hogar")
    hogar = models.ForeignKey(HogarComunitario, on_delete=models.PROTECT, related_name='ninos')
    padre = models.ForeignKey(Padre, on_delete=models.CASCADE, related_name='ninos')
    foto = models.FileField(upload_to='ninos/fotos/', null=True, blank=True)
    carnet_vacunacion = models.FileField(upload_to='ninos/vacunacion/', null=True, blank=True)
    certificado_eps = models.FileField(upload_to='ninos/eps/', null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registro_civil_img = models.FileField(upload_to='ninos/registro_civil/', null=True, blank=True)
    
    # Campos adicionales
    observaciones_medicas = models.TextField(null=True, blank=True, verbose_name="Observaciones médicas")
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('inactivo', 'Inactivo'),
            ('retirado', 'Retirado')
        ],
        default='activo'
    )

    class Meta:
        db_table = 'ninos'

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


# ------------------------
# Asistencia
# ------------------------
class Asistencia(models.Model):
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, related_name='asistencias')
    fecha = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Presente', 'Presente'),
            ('Ausente', 'Ausente'),
            ('Justificado', 'Justificado')
        ]
    )

    class Meta:
        db_table = 'asistencia'
        indexes = [models.Index(fields=['nino'])]

    def __str__(self):
        return f"Asistencia {self.nino} - {self.fecha} : {self.estado}"

# ------------------------
# Planeación
# ------------------------
class Planeacion(models.Model):
    fecha = models.DateField()
    nombre_actividad = models.CharField(max_length=150)
    intencionalidad_pedagogica = models.TextField()
    materiales_utilizar = models.TextField(null=True, blank=True)
    ambientacion = models.TextField(null=True, blank=True)
    actividad_inicio = models.TextField(null=True, blank=True)
    desarrollo = models.TextField(null=True, blank=True)
    cierre = models.TextField(null=True, blank=True)
    documentacion = models.TextField(null=True, blank=True)
    observacion = models.TextField(null=True, blank=True)
    hogar = models.ForeignKey(HogarComunitario, on_delete=models.CASCADE, related_name='planeaciones')

    class Meta:
        db_table = 'planeaciones'

    def __str__(self):
        return f"{self.nombre_actividad} - {self.fecha}"

# ------------------------
# Solicitud de Matriculación
# ------------------------
class SolicitudMatriculacion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('correccion', 'En Corrección'),
        ('cancelado_expiracion', 'Cancelado por Expiración'),
        ('cancelado_usuario', 'Cancelado por Usuario'),
        ('token_usado', 'Token Usado'),
    ]
    
    hogar = models.ForeignKey(HogarComunitario, on_delete=models.CASCADE, related_name='solicitudes_matricula')
    email_acudiente = models.EmailField(max_length=100)
    token = models.CharField(max_length=100, unique=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendiente')
    
    # Datos del niño
    nombres_nino = models.CharField(max_length=100, null=True, blank=True)
    apellidos_nino = models.CharField(max_length=100, null=True, blank=True)
    documento_nino = models.CharField(max_length=50, null=True, blank=True)
    fecha_nacimiento_nino = models.DateField(null=True, blank=True)
    genero_nino = models.CharField(max_length=20, null=True, blank=True)
    tipo_sangre_nino = models.CharField(max_length=5, null=True, blank=True)
    parentesco = models.CharField(max_length=50, null=True, blank=True)
    observaciones_nino = models.TextField(null=True, blank=True)
    
    # Discapacidad del niño
    tiene_discapacidad = models.BooleanField(default=False, null=True, blank=True)
    tipos_discapacidad = models.JSONField(null=True, blank=True)  # Lista de IDs de discapacidades
    otra_discapacidad = models.CharField(max_length=100, null=True, blank=True)
    
    # Documentos del niño
    foto_nino = models.FileField(upload_to='solicitudes/ninos/fotos/', null=True, blank=True)
    carnet_vacunacion_nino = models.FileField(upload_to='solicitudes/ninos/vacunacion/', null=True, blank=True)
    certificado_eps_nino = models.FileField(upload_to='solicitudes/ninos/eps/', null=True, blank=True)
    registro_civil_nino = models.FileField(upload_to='solicitudes/ninos/registro_civil/', null=True, blank=True)
    
    # Datos del padre
    tipo_documento_padre = models.CharField(max_length=5, null=True, blank=True)
    documento_padre = models.CharField(max_length=50, null=True, blank=True)
    nombres_padre = models.CharField(max_length=100, null=True, blank=True)
    apellidos_padre = models.CharField(max_length=100, null=True, blank=True)
    correo_padre = models.EmailField(max_length=100, null=True, blank=True)
    telefono_padre = models.CharField(max_length=20, null=True, blank=True)
    
    # 🆕 Ubicación geográfica del padre
    departamento_padre = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, blank=True, related_name='padres_solicitantes')
    ciudad_padre = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True, related_name='padres_solicitantes')
    localidad_bogota_padre = models.ForeignKey(LocalidadBogota, on_delete=models.SET_NULL, null=True, blank=True, related_name='padres_solicitantes',
                                                help_text='Solo si vive en Bogotá D.C.')
    
    direccion_padre = models.CharField(max_length=200, null=True, blank=True)
    barrio_padre = models.CharField(max_length=100, null=True, blank=True)
    ocupacion_padre = models.CharField(max_length=100, null=True, blank=True)
    nivel_educativo_padre = models.CharField(max_length=50, null=True, blank=True)
    
    # Contraseña para el padre
    password_padre = models.CharField(max_length=255, null=True, blank=True)
    
    # Documentos del padre
    documento_identidad_padre = models.FileField(upload_to='solicitudes/padres/cedulas/', null=True, blank=True)
    clasificacion_sisben_padre = models.FileField(upload_to='solicitudes/padres/sisben/', null=True, blank=True)
    
    # Campos para corrección y rechazo
    campos_corregir = models.JSONField(null=True, blank=True)  # Lista de campos a corregir
    motivo_rechazo = models.TextField(null=True, blank=True)
    intentos_correccion = models.IntegerField(default=0)  # Contador de intentos de corrección
    
    # Fechas de seguimiento
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_rechazo = models.DateTimeField(null=True, blank=True)
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)
    motivo_cancelacion = models.TextField(null=True, blank=True)  # Razón de cancelación
    
    class Meta:
        db_table = 'solicitudes_matriculacion'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Solicitud {self.id} - {self.email_acudiente} ({self.estado})"
    
    def is_valido(self):
        """Verifica si el token aún es válido"""
        from django.utils import timezone
        # Token válido solo si no está en estados terminales
        estados_terminales = ['aprobado', 'rechazado', 'cancelado_expiracion', 'cancelado_usuario', 'token_usado']
        return timezone.now() < self.fecha_expiracion and self.estado not in estados_terminales
    
    def cancelar_por_expiracion(self):
        """Cancela la solicitud por expiración del token"""
        from django.utils import timezone
        if self.estado in ['pendiente', 'correccion']:
            self.estado = 'cancelado_expiracion'
            self.fecha_cancelacion = timezone.now()
            self.motivo_cancelacion = f'Token expirado el {self.fecha_expiracion.strftime("%d/%m/%Y %H:%M")}'
            self.save()
            return True
        return False
    
    def cancelar_por_usuario(self, motivo=''):
        """Permite al usuario cancelar su solicitud"""
        from django.utils import timezone
        if self.estado in ['pendiente', 'correccion']:
            self.estado = 'cancelado_usuario'
            self.fecha_cancelacion = timezone.now()
            self.motivo_cancelacion = motivo or 'Cancelado por el usuario'
            self.save()
            return True
        return False
    
    def marcar_token_usado(self):
        """Marca el token como usado después de aprobar la solicitud"""
        from django.utils import timezone
        if self.estado == 'aprobado':
            self.estado = 'token_usado'
            self.save()
            return True
        return False
    
    def delete(self, *args, **kwargs):
        """Elimina archivos asociados antes de borrar la solicitud"""
        import os
        
        # Lista de campos FileField a limpiar
        campos_archivo = [
            'foto_nino',
            'carnet_vacunacion_nino',
            'certificado_eps_nino',
            'registro_civil_nino',
            'documento_identidad_padre',
            'clasificacion_sisben_padre',
        ]
        
        # Eliminar cada archivo asociado
        for campo in campos_archivo:
            archivo = getattr(self, campo, None)
            if archivo and archivo.name:
                try:
                    if os.path.exists(archivo.path):
                        os.remove(archivo.path)
                except Exception as e:
                    # Log del error pero continuar con la eliminación
                    print(f"Error al eliminar {campo}: {e}")
        
        # Eliminar notificaciones asociadas (cascade automático via signals)
        # Llamar al delete original
        super().delete(*args, **kwargs)

# ------------------------
# Historial de Cambios
# ------------------------
class HistorialCambio(models.Model):
    """Registra todos los cambios realizados en solicitudes y niños para auditoría"""
    TIPO_MODELO_CHOICES = [
        ('solicitud', 'Solicitud de Matriculación'),
        ('nino', 'Niño'),
        ('padre', 'Padre/Acudiente'),
    ]
    
    # Relación con el objeto modificado
    tipo_modelo = models.CharField(max_length=20, choices=TIPO_MODELO_CHOICES)
    objeto_id = models.PositiveIntegerField()  # ID del objeto modificado
    
    # Información del cambio
    campo_modificado = models.CharField(max_length=100)  # Nombre del campo que cambió
    valor_anterior = models.TextField(null=True, blank=True)  # Valor antes del cambio
    valor_nuevo = models.TextField(null=True, blank=True)  # Valor después del cambio
    
    # Información de auditoría
    accion = models.CharField(max_length=50, default='modificacion')  # crear, modificar, eliminar, corregir
    usuario = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(null=True, blank=True)  # Contexto adicional
    
    class Meta:
        db_table = 'historial_cambios'
        ordering = ['-fecha_cambio']
        indexes = [
            models.Index(fields=['tipo_modelo', 'objeto_id']),
            models.Index(fields=['fecha_cambio']),
        ]
    
    def __str__(self):
        return f"{self.tipo_modelo} #{self.objeto_id} - {self.campo_modificado} - {self.fecha_cambio.strftime('%Y-%m-%d %H:%M')}"
    
# ------------------------ JUANITO ------------------------
# sistema de notificaciones 
#User = get_user_model() bro cnacelado por el bien de la trama, mas que cree ya notificaciones en su propio app

#class Notification(models.Model):
    #title = models.CharField(max_length=200)
    #message = models.TextField()
    #level = models.CharField(
        max_length=20,
        choices=[("grave", "Grave"), ("warning", "Warning"), ("info", "Info")],
        default="info",
    #)
    #created_at = models.DateTimeField(auto_now_add=True)
    #read = models.BooleanField(default=False)

    # Opcional: destinatario(s)
    #recipient = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="core_notifications_received"
    #)

    #content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="core_notifications_content"
    #)
    #object_id = models.PositiveIntegerField(null=True, blank=True)
    #related_object = GenericForeignKey("content_type", "object_id")

    #class Meta:
        ordering = ["-created_at"]

    #def __str__(self):
        return f"{self.title} ({self.level})"


# ========================================================================================
# 🏠 SISTEMA DE VISITAS TÉCNICAS PARA HABILITACIÓN DE HOGARES
# ========================================================================================

class VisitaTecnica(models.Model):
    """
    Modelo para agendar visitas técnicas de habilitación a hogares comunitarios.
    Primera visita (V1) para evaluar condiciones antes de activar el hogar.
    """
    hogar = models.ForeignKey(
        HogarComunitario, 
        on_delete=models.CASCADE, 
        related_name='visitas_tecnicas'
    )
    
    # Información de la visita
    fecha_programada = models.DateTimeField()
    visitador = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='visitas_realizadas',
        limit_choices_to={'rol__nombre_rol': 'administrador'}
    )
    
    # Estados de la visita
    ESTADO_CHOICES = [
        ('agendada', 'Agendada'),
        ('en_proceso', 'En Proceso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('reprogramada', 'Reprogramada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='agendada')
    
    # Tipo de visita
    TIPO_CHOICES = [
        ('V1', 'Primera Visita - Habilitación'),
        ('V2', 'Visita de Seguimiento'),
        ('V3', 'Visita Extraordinaria'),
    ]
    tipo_visita = models.CharField(max_length=3, choices=TIPO_CHOICES, default='V1')
    
    # Observaciones y seguimiento
    observaciones_agenda = models.TextField(null=True, blank=True, help_text="Observaciones al agendar la visita")
    fecha_realizacion = models.DateTimeField(null=True, blank=True)
    
    # Notificaciones
    correo_enviado = models.BooleanField(default=False)
    fecha_envio_correo = models.DateTimeField(null=True, blank=True)
    
    # Auditoría
    creado_por = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='visitas_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'visitas_tecnicas'
        verbose_name = 'Visita Técnica'
        verbose_name_plural = 'Visitas Técnicas'
        ordering = ['-fecha_programada']
    
    def __str__(self):
        return f"{self.tipo_visita} - {self.hogar.nombre_hogar} - {self.fecha_programada.strftime('%d/%m/%Y')}"


class ActaVisitaTecnica(models.Model):
    """
    Acta de Visita Técnica (V1) - Registro completo de la evaluación del hogar.
    Contiene toda la información solicitada para validar la habilitación.
    """
    visita = models.OneToOneField(
        VisitaTecnica, 
        on_delete=models.CASCADE, 
        related_name='acta'
    )
    
    # ============================================
    # A. GEOLOCALIZACIÓN Y CONFIRMACIÓN DE DIRECCIÓN
    # ============================================
    geolocalizacion_lat_verificada = models.DecimalField(
        max_digits=10, decimal_places=7,
        help_text="Latitud capturada en el momento de la visita"
    )
    geolocalizacion_lon_verificada = models.DecimalField(
        max_digits=10, decimal_places=7,
        help_text="Longitud capturada en el momento de la visita"
    )
    
    direccion_verificada = models.CharField(max_length=200)
    direccion_coincide = models.BooleanField(
        default=False,
        help_text="¿La dirección verificada coincide con la reportada en el FUR?"
    )
    observaciones_direccion = models.TextField(null=True, blank=True)
    
    estrato_verificado = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        help_text="Estrato confirmado del recibo de servicio público"
    )
    estrato_coincide = models.BooleanField(default=False)
    foto_recibo_servicio = models.ImageField(
        upload_to='visitas/recibos/',
        help_text="Foto del recibo de servicio público para verificar estrato"
    )
    
    # ============================================
    # B. SERVICIOS Y SEGURIDAD
    # ============================================
    # Servicios Básicos
    tiene_agua_potable = models.BooleanField(default=False)
    agua_continua = models.BooleanField(default=False, help_text="Suministro continuo")
    agua_legal = models.BooleanField(default=False, help_text="Conexión legal")
    
    tiene_energia = models.BooleanField(default=False)
    energia_continua = models.BooleanField(default=False)
    energia_legal = models.BooleanField(default=False)
    
    tiene_alcantarillado = models.BooleanField(default=False)
    manejo_excretas_adecuado = models.BooleanField(
        default=False, 
        help_text="Si no hay alcantarillado, ¿hay manejo adecuado de excretas?"
    )
    
    # Infraestructura
    ESTADO_CHOICES = [
        ('excelente', 'Excelente'),
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('malo', 'Malo'),
        ('muy_malo', 'Muy Malo'),
    ]
    
    estado_pisos = models.CharField(max_length=15, choices=ESTADO_CHOICES)
    estado_paredes = models.CharField(max_length=15, choices=ESTADO_CHOICES)
    estado_techos = models.CharField(max_length=15, choices=ESTADO_CHOICES)
    
    ventilacion_adecuada = models.BooleanField(default=False)
    iluminacion_natural_adecuada = models.BooleanField(default=False)
    
    observaciones_infraestructura = models.TextField(null=True, blank=True)
    
    # Riesgos Ambientales
    NIVEL_RIESGO_CHOICES = [
        ('sin_riesgo', 'Sin Riesgo'),
        ('riesgo_bajo', 'Riesgo Bajo'),
        ('riesgo_medio', 'Riesgo Medio'),
        ('riesgo_alto', 'Riesgo Alto'),
        ('riesgo_critico', 'Riesgo Crítico'),
    ]
    
    proximidad_rios = models.BooleanField(default=False)
    proximidad_deslizamientos = models.BooleanField(default=False)
    proximidad_trafico_intenso = models.BooleanField(default=False)
    proximidad_contaminacion = models.BooleanField(default=False)
    
    nivel_riesgo_general = models.CharField(
        max_length=20, 
        choices=NIVEL_RIESGO_CHOICES,
        default='sin_riesgo'
    )
    
    descripcion_riesgos = models.TextField(
        null=True, blank=True,
        help_text="Descripción detallada de los riesgos identificados"
    )
    
    # ============================================
    # C. ESPACIOS ESPECÍFICOS PARA CÁLCULO DE CAPACIDAD
    # ============================================
    # Áreas Sociales (Salas de cuidado)
    area_social_largo = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Largo del área social en metros"
    )
    area_social_ancho = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Ancho del área social en metros"
    )
    area_social_total = models.DecimalField(
        max_digits=7, decimal_places=2,
        null=True, blank=True,
        help_text="Área total calculada (largo x ancho)"
    )
    foto_area_social_medidas = models.ImageField(
        upload_to='visitas/areas_sociales/',
        help_text="Foto del área social mostrando las medidas"
    )
    
    # Patio Cubierto (si aplica)
    tiene_patio_cubierto = models.BooleanField(default=False)
    patio_largo = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    patio_ancho = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    patio_total = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    foto_patio_medidas = models.ImageField(
        upload_to='visitas/patios/',
        null=True, blank=True
    )
    
    # Baños
    num_banos_verificado = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Cantidad de baños/baterías sanitarias"
    )
    
    ESTADO_HIGIENE_CHOICES = [
        ('excelente', 'Excelente'),
        ('bueno', 'Bueno'),
        ('aceptable', 'Aceptable'),
        ('deficiente', 'Deficiente'),
        ('inaceptable', 'Inaceptable'),
    ]
    
    estado_higiene_banos = models.CharField(
        max_length=15, 
        choices=ESTADO_HIGIENE_CHOICES
    )
    
    foto_bano_1 = models.ImageField(
        upload_to='visitas/banos/',
        help_text="Foto del baño principal"
    )
    foto_bano_2 = models.ImageField(
        upload_to='visitas/banos/',
        null=True, blank=True,
        help_text="Foto de baño adicional (si hay más de uno)"
    )
    
    # Fachada
    foto_fachada = models.ImageField(
        upload_to='visitas/fachadas/',
        help_text="Foto de la fachada de la casa"
    )
    foto_fachada_numeracion = models.ImageField(
        upload_to='visitas/fachadas/',
        null=True, blank=True,
        help_text="Foto de la numeración de la casa"
    )
    
    # ============================================
    # D. CÁLCULO DE CAPACIDAD RECOMENDADA
    # ============================================
    capacidad_calculada = models.IntegerField(
        null=True, blank=True,
        help_text="Capacidad calculada según el área disponible (1.5m² por niño)"
    )
    capacidad_recomendada = models.IntegerField(
        help_text="Capacidad recomendada por el visitador"
    )
    justificacion_capacidad = models.TextField(
        null=True, blank=True,
        help_text="Justificación de la capacidad recomendada"
    )
    
    # ============================================
    # E. RESULTADO Y CONCLUSIÓN
    # ============================================
    RESULTADO_CHOICES = [
        ('aprobado', 'Aprobado'),
        ('aprobado_condiciones', 'Aprobado con Condiciones'),
        ('rechazado', 'Rechazado'),
        ('requiere_segunda_visita', 'Requiere Segunda Visita'),
    ]
    
    resultado_visita = models.CharField(
        max_length=30,
        choices=RESULTADO_CHOICES
    )
    
    observaciones_generales = models.TextField(help_text="Observaciones y conclusiones de la visita")
    recomendaciones = models.TextField(null=True, blank=True)
    condiciones_aprobacion = models.TextField(
        null=True, blank=True,
        help_text="Condiciones que debe cumplir si es aprobado con condiciones"
    )
    
    # Firma del visitador
    firma_visitador = models.ImageField(
        upload_to='visitas/firmas/',
        null=True, blank=True,
        help_text="Firma digital del visitador"
    )
    
    # Firma de la madre (conformidad)
    firma_madre = models.ImageField(
        upload_to='visitas/firmas/',
        null=True, blank=True,
        help_text="Firma de la madre comunitaria"
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    completado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='actas_completadas'
    )
    
    class Meta:
        db_table = 'actas_visitas_tecnicas'
        verbose_name = 'Acta de Visita Técnica'
        verbose_name_plural = 'Actas de Visitas Técnicas'
    
    def __str__(self):
        return f"Acta {self.visita.tipo_visita} - {self.visita.hogar.nombre_hogar}"
    
    def save(self, *args, **kwargs):
        # Calcular área total automáticamente
        if self.area_social_largo and self.area_social_ancho:
            self.area_social_total = self.area_social_largo * self.area_social_ancho
        
        if self.tiene_patio_cubierto and self.patio_largo and self.patio_ancho:
            self.patio_total = self.patio_largo * self.patio_ancho
        
        # Calcular capacidad según normativa (1.5m² por niño)
        if self.area_social_total:
            area_total = float(self.area_social_total)
            if self.patio_total:
                area_total += float(self.patio_total)
            self.capacidad_calculada = int(area_total / 1.5)
        
        super().save(*args, **kwargs)