from django.db.models.signals import post_migrate, pre_save, post_save
from django.dispatch import receiver
from core.models import Rol, SolicitudMatriculacion, Nino, Padre, HistorialCambio
from django.utils import timezone

@receiver(post_migrate)
def crear_roles_iniciales(sender, **kwargs):
    if sender.name == 'core':
        roles = ['administrador', 'madre_comunitaria', 'padre']
        for nombre in roles:
            Rol.objects.get_or_create(nombre_rol=nombre)

# ------------------------
# Señales para Historial de Cambios
# ------------------------

# Diccionario para almacenar valores anteriores
_valores_anteriores = {}

@receiver(pre_save, sender=SolicitudMatriculacion)
def guardar_estado_anterior_solicitud(sender, instance, **kwargs):
    """Guarda el estado anterior de la solicitud antes de modificarla"""
    if instance.pk:  # Solo si ya existe
        try:
            anterior = SolicitudMatriculacion.objects.get(pk=instance.pk)
            _valores_anteriores[f'solicitud_{instance.pk}'] = {
                'nombres_nino': anterior.nombres_nino,
                'apellidos_nino': anterior.apellidos_nino,
                'documento_nino': anterior.documento_nino,
                'fecha_nacimiento_nino': str(anterior.fecha_nacimiento_nino) if anterior.fecha_nacimiento_nino else None,
                'genero_nino': anterior.genero_nino,
                'tipo_sangre_nino': anterior.tipo_sangre_nino,
                'tiene_discapacidad': anterior.tiene_discapacidad,
                'tipos_discapacidad': anterior.tipos_discapacidad,
                'otra_discapacidad': anterior.otra_discapacidad,
                'nombres_padre': anterior.nombres_padre,
                'apellidos_padre': anterior.apellidos_padre,
                'documento_padre': anterior.documento_padre,
                'correo_padre': anterior.correo_padre,
                'telefono_padre': anterior.telefono_padre,
                'direccion_padre': anterior.direccion_padre,
                'ocupacion_padre': anterior.ocupacion_padre,
                'estado': anterior.estado,
                'campos_corregir': anterior.campos_corregir,
                'intentos_correccion': anterior.intentos_correccion,
            }
        except SolicitudMatriculacion.DoesNotExist:
            pass

@receiver(post_save, sender=SolicitudMatriculacion)
def registrar_cambios_solicitud(sender, instance, created, **kwargs):
    """Registra los cambios en el historial después de guardar"""
    if created:
        # Registro de creación
        HistorialCambio.objects.create(
            tipo_modelo='solicitud',
            objeto_id=instance.pk,
            campo_modificado='creacion',
            valor_nuevo='Solicitud creada',
            accion='crear',
            observaciones=f'Nueva solicitud para {instance.email_acudiente}'
        )
    else:
        # Comparar valores anteriores con actuales
        key = f'solicitud_{instance.pk}'
        if key in _valores_anteriores:
            anterior = _valores_anteriores[key]
            
            # Campos a monitorear
            campos_monitorear = {
                'nombres_nino': 'Nombres del Niño',
                'apellidos_nino': 'Apellidos del Niño',
                'documento_nino': 'Documento del Niño',
                'fecha_nacimiento_nino': 'Fecha de Nacimiento',
                'genero_nino': 'Género',
                'tipo_sangre_nino': 'Tipo de Sangre',
                'tiene_discapacidad': 'Tiene Discapacidad',
                'tipos_discapacidad': 'Tipos de Discapacidad',
                'otra_discapacidad': 'Otra Discapacidad',
                'nombres_padre': 'Nombres del Acudiente',
                'apellidos_padre': 'Apellidos del Acudiente',
                'documento_padre': 'Documento del Acudiente',
                'correo_padre': 'Correo del Acudiente',
                'telefono_padre': 'Teléfono del Acudiente',
                'direccion_padre': 'Dirección',
                'ocupacion_padre': 'Ocupación',
                'estado': 'Estado',
                'intentos_correccion': 'Intentos de Corrección',
            }
            
            for campo, nombre_legible in campos_monitorear.items():
                valor_actual = getattr(instance, campo)
                if campo == 'fecha_nacimiento_nino' and valor_actual:
                    valor_actual = str(valor_actual)
                    
                if anterior.get(campo) != valor_actual:
                    # Determinar la acción
                    accion = 'modificacion'
                    if campo == 'estado':
                        if valor_actual == 'correccion':
                            accion = 'corregir'
                        elif valor_actual == 'aprobado':
                            accion = 'aprobar'
                        elif valor_actual == 'rechazado':
                            accion = 'rechazar'
                    
                    HistorialCambio.objects.create(
                        tipo_modelo='solicitud',
                        objeto_id=instance.pk,
                        campo_modificado=nombre_legible,
                        valor_anterior=str(anterior.get(campo)) if anterior.get(campo) else 'Vacío',
                        valor_nuevo=str(valor_actual) if valor_actual else 'Vacío',
                        accion=accion,
                        observaciones=f'Campo modificado en solicitud #{instance.pk}'
                    )
            
            # Limpiar valores anteriores
            del _valores_anteriores[key]

@receiver(pre_save, sender=Nino)
def guardar_estado_anterior_nino(sender, instance, **kwargs):
    """Guarda el estado anterior del niño antes de modificarlo"""
    if instance.pk:
        try:
            anterior = Nino.objects.get(pk=instance.pk)
            _valores_anteriores[f'nino_{instance.pk}'] = {
                'nombres': anterior.nombres,
                'apellidos': anterior.apellidos,
                'documento': anterior.documento,
                'fecha_nacimiento': str(anterior.fecha_nacimiento) if anterior.fecha_nacimiento else None,
                'genero': anterior.genero,
                'tipo_sangre': anterior.tipo_sangre,
                'estado': anterior.estado,
                'observaciones_medicas': anterior.observaciones_medicas,
            }
        except Nino.DoesNotExist:
            pass

@receiver(post_save, sender=Nino)
def registrar_cambios_nino(sender, instance, created, **kwargs):
    """Registra los cambios en el historial del niño"""
    if created:
        HistorialCambio.objects.create(
            tipo_modelo='nino',
            objeto_id=instance.pk,
            campo_modificado='creacion',
            valor_nuevo=f'{instance.nombres} {instance.apellidos}',
            accion='crear',
            observaciones=f'Niño matriculado en {instance.hogar.nombre_hogar}'
        )
    else:
        key = f'nino_{instance.pk}'
        if key in _valores_anteriores:
            anterior = _valores_anteriores[key]
            
            campos_monitorear = {
                'nombres': 'Nombres',
                'apellidos': 'Apellidos',
                'documento': 'Documento',
                'fecha_nacimiento': 'Fecha de Nacimiento',
                'genero': 'Género',
                'tipo_sangre': 'Tipo de Sangre',
                'estado': 'Estado',
                'observaciones_medicas': 'Observaciones Médicas',
            }
            
            for campo, nombre_legible in campos_monitorear.items():
                valor_actual = getattr(instance, campo)
                if campo == 'fecha_nacimiento' and valor_actual:
                    valor_actual = str(valor_actual)
                    
                if anterior.get(campo) != valor_actual:
                    HistorialCambio.objects.create(
                        tipo_modelo='nino',
                        objeto_id=instance.pk,
                        campo_modificado=nombre_legible,
                        valor_anterior=str(anterior.get(campo)) if anterior.get(campo) else 'Vacío',
                        valor_nuevo=str(valor_actual) if valor_actual else 'Vacío',
                        accion='modificacion',
                        observaciones=f'Campo modificado para {instance.nombres} {instance.apellidos}'
                    )
            
            del _valores_anteriores[key]

