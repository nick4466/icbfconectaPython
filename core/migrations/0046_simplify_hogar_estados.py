# Generated migration for estado simplification

from django.db import migrations, models


def migrate_estados_forward(apps, schema_editor):
    """Migra los estados existentes al nuevo modelo simplificado"""
    HogarComunitario = apps.get_model('core', 'HogarComunitario')
    
    # Mapeo de estados antiguos a nuevos
    state_mapping = {
        'pendiente_revision': 'pendiente_visita',
        'en_revision': 'visitando',
        'aprobado': 'activo',
        'rechazado': 'rechazado',
        'en_mantenimiento': 'visitando',
        'pendiente_visita': 'pendiente_visita',
        'visita_agendada': 'visitando',
        'en_evaluacion': 'visitando',
        'activo': 'activo',
        'inactivo': 'rechazado',
    }
    
    for hogar in HogarComunitario.objects.all():
        new_estado = state_mapping.get(hogar.estado, 'pendiente_visita')
        if hogar.estado != new_estado:
            hogar.estado = new_estado
            hogar.save(update_fields=['estado'])


def migrate_estados_backward(apps, schema_editor):
    """Revierte la migración de estados (usamos estado más cercano)"""
    HogarComunitario = apps.get_model('core', 'HogarComunitario')
    
    # Mapeo inverso (imperfecto pero mejor que nada)
    state_mapping = {
        'pendiente_visita': 'pendiente_visita',
        'visitando': 'en_revision',
        'activo': 'activo',
        'rechazado': 'rechazado',
    }
    
    for hogar in HogarComunitario.objects.all():
        new_estado = state_mapping.get(hogar.estado, 'pendiente_visita')
        if hogar.estado != new_estado:
            hogar.estado = new_estado
            hogar.save(update_fields=['estado'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0045_crear_solicitud_retiro_matricula'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hogarcomunitario',
            name='estado',
            field=models.CharField(
                choices=[
                    ('pendiente_visita', 'Pendiente de Visita'),
                    ('visitando', 'Visitando'),
                    ('activo', 'Activo'),
                    ('rechazado', 'Rechazado'),
                ],
                default='pendiente_visita',
                help_text='Estado del hogar en el ciclo de visita técnica',
                max_length=30,
            ),
        ),
        migrations.RunPython(migrate_estados_forward, migrate_estados_backward),
    ]
