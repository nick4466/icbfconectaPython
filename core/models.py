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

def madre_upload_path(instance, filename):
    return f"madres_documentos/{instance.usuario.documento}/{filename}"


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
    username = None


    tipo_documento = models.CharField(max_length=5, choices=TIPO_DOCUMENTO_CHOICES, default='CC')
    documento = models.BigIntegerField(unique=True)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    correo = models.EmailField(max_length=100, unique=True)
    direccion = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True)
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

    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='padre_profile')
    ocupacion = models.CharField(max_length=50, null=True, blank=True)
    estrato = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(6)])

    telefono_contacto_emergencia = models.CharField(max_length=20, null=True, blank=True)
    nombre_contacto_emergencia = models.CharField(max_length=100, null=True, blank=True)
    situacion_economica_hogar = models.CharField(max_length=100, null=True, blank=True)
    documento_identidad_img = models.CharField(max_length=255, null=True, blank=True)

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

    # Información académica y experiencia
    nivel_escolaridad = models.CharField(max_length=100, choices=[
        ('Primaria', 'Primaria'),
        ('Bachiller', 'Bachiller'),
        ('Técnico', 'Técnico'),
        ('Tecnólogo', 'Tecnólogo'),
        ('Profesional', 'Profesional')
    ])
    titulo_obtenido = models.CharField(max_length=150, null=True, blank=True)
    institucion = models.CharField(max_length=150, null=True, blank=True)
    experiencia_previa = models.TextField(null=True, blank=True)

    # Declaraciones
    no_retirado_icbf = models.BooleanField(default=False)
    disponibilidad_tiempo = models.BooleanField(default=False)
    firma_digital = models.FileField(upload_to='madres_documentos/firmas/', null=True, blank=True)

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
    nombre_hogar = models.CharField(max_length=100)
    direccion = models.CharField(max_length=150)
    localidad = models.CharField(max_length=50, null=True, blank=True)
    ciudad = models.CharField(max_length=100, null=True, blank=True)
    barrio = models.CharField(max_length=100, null=True, blank=True)
    estrato = models.IntegerField(null=True, blank=True)

    # Infraestructura
    num_habitaciones = models.IntegerField(null=True, blank=True)
    num_banos = models.IntegerField(null=True, blank=True)
    material_construccion = models.CharField(max_length=100, null=True, blank=True)
    riesgos_cercanos = models.TextField(null=True, blank=True)

    # Fotos y geolocalización
    fotos_interior = models.FileField(upload_to='hogares/fotos_interior/', null=True, blank=True)
    fotos_exterior = models.FileField(upload_to='hogares/fotos_exterior/', null=True, blank=True)
    geolocalizacion_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    geolocalizacion_lon = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Tenencia del inmueble
    tipo_tenencia = models.CharField(max_length=50, choices=[
        ('Propia', 'Propia'),
        ('Arrendada', 'Arrendada'),
        ('Comodato', 'Comodato')
    ], null=True, blank=True)
    documento_tenencia_pdf = models.FileField(upload_to='hogares/documentos_tenencia/', null=True, blank=True)

    # Estado y relación
    capacidad_maxima = models.IntegerField(default=20)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'activo'),
            ('inactivo', 'inactivo'),
            ('en_mantenimiento', 'en_mantenimiento')
        ],
        default='activo'
    )
    madre = models.ForeignKey(MadreComunitaria, on_delete=models.PROTECT, related_name='hogares_asignados')

    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hogares_comunitarios'

    def __str__(self):
        return self.nombre_hogar
# ------------------------
# Convivientes del Hogar Comunitario
# ------------------------
class ConvivienteHogar(models.Model):
    hogar = models.ForeignKey(HogarComunitario, on_delete=models.CASCADE, related_name='convivientes')
    nombre = models.CharField(max_length=100)
    cedula = models.BigIntegerField()
    edad = models.IntegerField()
    parentesco = models.CharField(max_length=50)

    class Meta:
        db_table = 'convivientes_hogar'

    def __str__(self):
        return f"{self.nombre} ({self.parentesco}) - Hogar: {self.hogar.nombre_hogar}"


# ------------------------
# Niños
# ------------------------
class Nino(models.Model):
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
    nacionalidad = models.CharField(max_length=50, null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    hogar = models.ForeignKey(HogarComunitario, on_delete=models.PROTECT, related_name='ninos')
    padre = models.ForeignKey(Padre, on_delete=models.CASCADE, related_name='ninos')
    foto = models.FileField(upload_to='ninos/fotos/', null=True, blank=True)
    carnet_vacunacion = models.FileField(upload_to='ninos/vacunacion/', null=True, blank=True)
    certificado_eps = models.FileField(upload_to='ninos/eps/', null=True, blank=True)

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
# Desarrollo del Niño
# ------------------------
class DesarrolloNino(models.Model):
    nino = models.ForeignKey(Nino, on_delete=models.CASCADE, related_name='desarrollos')
    fecha_fin_mes = models.DateField()
    dimension_cognitiva = models.TextField(null=True, blank=True)
    dimension_comunicativa = models.TextField(null=True, blank=True)
    dimension_socio_afectiva = models.TextField(null=True, blank=True)
    dimension_corporal = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'desarrollo_nino'
        unique_together = (('nino', 'fecha_fin_mes'),)

    def __str__(self):
        return f"Desarrollo {self.nino} - {self.fecha_fin_mes}"


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
    
    
    
# ------------------------ JUANITO ------------------------
# Novedades
# Ajusta si el modelo Niño está en otra app
