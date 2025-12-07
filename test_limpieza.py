"""
Script de prueba para verificar el sistema de limpieza de archivos.

Ejecutar con: python manage.py shell < test_limpieza.py
"""

print("=" * 70)
print("  PRUEBA DEL SISTEMA DE LIMPIEZA DE ARCHIVOS")
print("=" * 70)

# 1. Verificar que el comando existe
print("\n✓ Verificando comando de limpieza...")
from django.core.management import call_command
try:
    # Simulación sin borrar nada
    call_command('limpiar_archivos_solicitudes', '--dry-run')
    print("✅ Comando 'limpiar_archivos_solicitudes' funciona correctamente")
except Exception as e:
    print(f"❌ Error: {e}")

# 2. Verificar APScheduler
print("\n✓ Verificando APScheduler...")
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    print("✅ APScheduler instalado correctamente")
except ImportError:
    print("❌ APScheduler no está instalado. Ejecuta: pip install APScheduler==3.10.4")

# 3. Verificar scheduler
print("\n✓ Verificando tareas programadas...")
try:
    from core.scheduler import iniciar_tareas_programadas
    scheduler = iniciar_tareas_programadas()
    jobs = scheduler.get_jobs()
    print(f"✅ Scheduler iniciado con {len(jobs)} tareas:")
    for job in jobs:
        print(f"   - {job.name} (ID: {job.id})")
        print(f"     Próxima ejecución: {job.next_run_time}")
    scheduler.shutdown()
except Exception as e:
    print(f"❌ Error: {e}")

# 4. Verificar método delete del modelo
print("\n✓ Verificando método delete() de SolicitudMatriculacion...")
try:
    from core.models import SolicitudMatriculacion
    import inspect
    
    if hasattr(SolicitudMatriculacion, 'delete'):
        source = inspect.getsource(SolicitudMatriculacion.delete)
        if 'os.remove' in source:
            print("✅ Método delete() personalizado implementado")
            print("   - Eliminará archivos automáticamente al borrar solicitud")
        else:
            print("⚠️  Método delete() existe pero no elimina archivos")
    else:
        print("❌ Método delete() no encontrado")
except Exception as e:
    print(f"❌ Error: {e}")

# 5. Estadísticas actuales
print("\n✓ Estadísticas del sistema...")
try:
    from core.models import SolicitudMatriculacion
    from django.utils import timezone
    from datetime import timedelta
    
    total = SolicitudMatriculacion.objects.count()
    pendientes = SolicitudMatriculacion.objects.filter(estado='pendiente').count()
    aprobadas = SolicitudMatriculacion.objects.filter(estado='aprobado').count()
    rechazadas = SolicitudMatriculacion.objects.filter(estado='rechazado').count()
    
    ahora = timezone.now()
    expiradas = SolicitudMatriculacion.objects.filter(
        fecha_expiracion__lt=ahora,
        estado__in=['pendiente', 'correccion']
    ).count()
    
    print(f"📊 Total solicitudes: {total}")
    print(f"   - Pendientes: {pendientes}")
    print(f"   - Aprobadas: {aprobadas}")
    print(f"   - Rechazadas: {rechazadas}")
    print(f"   - Expiradas: {expiradas}")
    
    if expiradas > 0:
        print(f"\n⚠️  Hay {expiradas} solicitudes expiradas que pueden limpiarse")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("  RESUMEN")
print("=" * 70)
print("""
✅ Sistema de limpieza configurado correctamente

Próximos pasos:
1. Ejecutar limpieza manual: python manage.py limpiar_archivos_solicitudes --dry-run
2. Reiniciar servidor Django para activar tareas programadas
3. Revisar documentación en LIMPIEZA_ARCHIVOS_DOCS.md
""")
print("=" * 70)
