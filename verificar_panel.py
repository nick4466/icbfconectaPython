#!/usr/bin/env python
"""Verificación final del Panel de Revisión"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from core.models import SolicitudMatriculacion, HogarComunitario

print("\n" + "="*80)
print("VERIFICACIÓN FINAL - PANEL DE REVISIÓN")
print("="*80)

# Verificar solicitudes pendientes por hogar
hogares = HogarComunitario.objects.all()

for hogar in hogares:
    print(f"\n🏠 Hogar: {hogar.nombre_hogar}")
    
    # Contar solicitudes pendientes y en corrección
    solicitudes_pendientes = SolicitudMatriculacion.objects.filter(
        hogar=hogar,
        estado__in=['pendiente', 'correccion']
    ).order_by('-fecha_creacion')
    
    print(f"   📊 Solicitudes pendientes/corrección: {solicitudes_pendientes.count()}")
    
    if solicitudes_pendientes.exists():
        print(f"\n   Detalle de solicitudes:")
        for s in solicitudes_pendientes:
            nombre = f"{s.nombres_nino or '[Sin completar]'}"
            tiene_datos = "✅ Completo" if s.nombres_nino else "⏳ Pendiente de completar"
            print(f"      • ID {s.id}: {nombre}")
            print(f"        Email: {s.email_acudiente}")
            print(f"        Estado: {s.estado}")
            print(f"        Formulario: {tiene_datos}")
            print(f"        Fecha: {s.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
            print()
    else:
        print("   ℹ️  No hay solicitudes pendientes")
    
    # Verificar si el hogar tiene madre
    if hogar.madre and hogar.madre.usuario:
        print(f"   👩 Madre: {hogar.madre.usuario.nombres} {hogar.madre.usuario.apellidos}")
        print(f"   📧 Email: {hogar.madre.usuario.correo}")
    else:
        print(f"   ⚠️  Este hogar no tiene madre asignada")

print("\n" + "="*80)
print("RESUMEN")
print("="*80)

total_pendientes = SolicitudMatriculacion.objects.filter(
    estado__in=['pendiente', 'correccion']
).count()

total_completadas = SolicitudMatriculacion.objects.filter(
    nombres_nino__isnull=False
).exclude(nombres_nino='').count()

total_sin_completar = SolicitudMatriculacion.objects.filter(
    estado__in=['pendiente', 'correccion']
).filter(
    nombres_nino__isnull=True
) | SolicitudMatriculacion.objects.filter(
    estado__in=['pendiente', 'correccion'],
    nombres_nino=''
)
total_sin_completar = total_sin_completar.count()

print(f"\n📋 Total solicitudes pendientes/corrección: {total_pendientes}")
print(f"✅ Solicitudes con formulario completo: {total_completadas}")
print(f"⏳ Solicitudes sin completar: {total_sin_completar}")

print("\n" + "="*80)
print("INSTRUCCIONES PARA VER EN EL PANEL")
print("="*80)
print("""
1. Inicia sesión como madre comunitaria
2. Ve a la página de 'Matrículas' (lista de niños)
3. Busca el botón verde 'Panel de Revisión'
4. El número rojo indica las solicitudes pendientes
5. Haz clic en el botón para abrir el panel

Las solicitudes aparecerán con:
- ✅ Formulario completo: Puedes aprobar, rechazar o solicitar correcciones
- ⏳ Pendiente: Esperando que el acudiente complete el formulario
""")

print("="*80 + "\n")
