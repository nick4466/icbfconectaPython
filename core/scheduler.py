"""
Configuración de tareas programadas para limpieza automática.

Ejecuta automáticamente:
- Limpieza de archivos basura diaria a las 3:00 AM
- Notificaciones de solicitudes por expirar
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def limpiar_archivos_basura():
    """Ejecuta el comando de limpieza de archivos"""
    try:
        logger.info("Iniciando limpieza automática de archivos basura...")
        call_command('limpiar_archivos_solicitudes', '--dias-rechazadas', '30', '--dias-sin-editar', '15')
        logger.info("Limpieza automática completada exitosamente")
    except Exception as e:
        logger.error(f"Error en limpieza automática: {e}")


def notificar_solicitudes_proximas_expirar():
    """Notifica sobre solicitudes que expiran pronto y cancela expiradas"""
    try:
        from core.models import SolicitudMatriculacion
        from datetime import timedelta
        from notifications.models import Notification
        
        logger.info("Verificando solicitudes próximas a expirar...")
        
        ahora = timezone.now()
        
        # 1. Cancelar solicitudes expiradas que aún están pendientes o en corrección
        solicitudes_expiradas = SolicitudMatriculacion.objects.filter(
            fecha_expiracion__lt=ahora,
            estado__in=['pendiente', 'correccion']
        )
        
        canceladas = 0
        for solicitud in solicitudes_expiradas:
            if solicitud.cancelar_por_expiracion():
                canceladas += 1
                logger.info(f"Solicitud {solicitud.id} cancelada por expiración")
        
        if canceladas > 0:
            logger.info(f"Se cancelaron {canceladas} solicitudes por expiración")
        
        # 2. Notificar sobre solicitudes que expiran pronto
        limite = ahora + timedelta(days=3)  # Avisar 3 días antes
        
        solicitudes = SolicitudMatriculacion.objects.filter(
            fecha_expiracion__gt=ahora,
            fecha_expiracion__lte=limite,
            estado__in=['pendiente', 'correccion']
        )
        
        for solicitud in solicitudes:
            # Crear notificación para la madre comunitaria
            dias_restantes = (solicitud.fecha_expiracion - ahora).days
            
            Notification.objects.get_or_create(
                solicitud=solicitud,
                tipo_notificacion='expiracion_proxima',
                defaults={
                    'usuario': solicitud.hogar.madre_comunitaria,
                    'mensaje': f'La solicitud de {solicitud.email_acudiente} expira en {dias_restantes} días',
                    'nivel': 'warning'
                }
            )
        
        logger.info(f"Se procesaron {solicitudes.count()} solicitudes próximas a expirar")
        
    except Exception as e:
        logger.error(f"Error en notificación de expiraciones: {e}")


def iniciar_tareas_programadas():
    """Inicia el scheduler con las tareas configuradas"""
    scheduler = BackgroundScheduler()
    
    # Limpieza diaria a las 3:00 AM
    scheduler.add_job(
        limpiar_archivos_basura,
        trigger=CronTrigger(hour=3, minute=0),
        id='limpieza_archivos_diaria',
        name='Limpieza diaria de archivos basura',
        replace_existing=True
    )
    
    # Verificar expiraciones cada día a las 9:00 AM
    scheduler.add_job(
        notificar_solicitudes_proximas_expirar,
        trigger=CronTrigger(hour=9, minute=0),
        id='notificar_expiraciones',
        name='Notificar solicitudes próximas a expirar',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Tareas programadas iniciadas correctamente")
    
    return scheduler
