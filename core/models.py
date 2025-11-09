from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# ------------------------
# Gestor de usuarios personalizado
# ------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, documento, email, password=None, **extra_fields):
        if not documento:
            raise ValueError('El campo Documento es obligatorio.')
        if not email:
            raise ValueError('El campo Email es obligatorio.')
        email = self.normalize_email(email)
        user = self.model(documento=documento, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, documento, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        rol_admin, _ = Rol.objects.get_or_create(nombre_rol='administrador')
        extra_fields['rol'] = rol_admin
        return self.create_user(documento, email, password, **extra_fields)


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
# Usuario personalizado
# ------------------------
class Usuario(AbstractUser):
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de ciudadanía'),
        ('TI', 'Tarjeta de identidad'),
        ('CE', 'Cédula de extranjería'),
        ('PA', 'Pasaporte'),
    ]

    tipo_documento = models.CharField(max_length=5, choices=TIPO_DOCUMENTO_CHOICES, default='CC')
    documento = models.BigIntegerField()
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)  # <--- Quitar unique=True
    direccion = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)

    USERNAME_FIELD = 'documento'
    REQUIRED_FIELDS = ['nombres', 'apellidos', 'email', 'tipo_documento']

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
    estrato = models.IntegerField(null=True, blank=True)
    telefono_contacto_emergencia = models.CharField(max_length=20, null=True, blank=True)
    nombre_contacto_emergencia = models.CharField(max_length=100, null=True, blank=True)
    situacion_economica_hogar = models.CharField(max_length=100, null=True, blank=True)
    documento_identidad_img = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'padres'

    def __str__(self):
        return f"Padre: {self.usuario.nombres} {self.usuario.apellidos}"


# ------------------------
# Hogares Comunitarios
# ------------------------
class HogarComunitario(models.Model):
    nombre_hogar = models.CharField(max_length=100)
    direccion = models.CharField(max_length=150, unique=True)
    localidad = models.CharField(max_length=50)
    capacidad_maxima = models.IntegerField(default=14)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'activo'),
            ('inactivo', 'inactivo'),
            ('en_mantenimiento', 'en_mantenimiento')
        ],
        default='activo'
    )
    madre = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='hogares_asignados')

    class Meta:
        db_table = 'hogares_comunitarios'

    def __str__(self):
        return self.nombre_hogar


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
            ('masculino', 'Masculino'),
            ('femenino', 'Femenino'),
            ('otro', 'Otro'),
            ('no_especificado', 'No especificado')
        ]
    )
    nacionalidad = models.CharField(max_length=50, null=True, blank=True)
    fecha_ingreso = models.DateField(null=True, blank=True)
    hogar = models.ForeignKey(HogarComunitario, on_delete=models.PROTECT, related_name='ninos')
    padre = models.ForeignKey(Padre, on_delete=models.CASCADE, related_name='ninos')
    foto = models.CharField(max_length=255, null=True, blank=True)
    carnet_vacunacion = models.CharField(max_length=255, null=True, blank=True)
    certificado_eps = models.CharField(max_length=255, null=True, blank=True)

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
        return f"{self.nombre_actividad} - {self.fecha}"
    
    
    
# ------------------------ JUANITO ------------------------
# Novedades
class Novedad(models.Model):
    fecha = models.DateField()
    realizada = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'novedades'
        ordering = ['-fecha']

    def __str__(self):
        estado = "Realizada" if self.realizada else "Pendiente"
        return f"{self.fecha} - {estado}"
