#!/usr/bin/env python
"""Script para verificar solicitudes y notificaciones"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from core.models import SolicitudMatriculacion, HogarComunitario
from notifications.models import Notification

print("=" * 80)
print("VERIFICACIÓN DE SOLICITUDES DE MATRÍCULA")
print("=" * 80)

# Verificar solicitudes
solicitudes = SolicitudMatriculacion.objects.all().order_by('-fecha_creacion')
print(f"\n📋 Total de solicitudes: {solicitudes.count()}")

if solicitudes.exists():
    print("\n🔍 Últimas 10 solicitudes:")
    for s in solicitudes[:10]:
        print(f"\n  ID: {s.id}")
        print(f"  Niño: {s.nombres_nino} {s.apellidos_nino}")
        print(f"  Email: {s.email_acudiente}")
        print(f"  Hogar: {s.hogar.nombre_hogar if s.hogar else 'Sin hogar'}")
        print(f"  Estado: {s.estado}")
        print(f"  Fecha creación: {s.fecha_creacion}")
        
        # Verificar si el hogar tiene madre
        if s.hogar:
            if hasattr(s.hogar, 'madre') and s.hogar.madre:
                print(f"  Madre: {s.hogar.madre.usuario.get_full_name()}")
                print(f"  Usuario madre: {s.hogar.madre.usuario.username}")
            else:
                print(f"  ⚠️ PROBLEMA: El hogar NO tiene madre asignada")
else:
    print("\n⚠️ NO HAY SOLICITUDES EN LA BASE DE DATOS")

print("\n" + "=" * 80)
print("VERIFICACIÓN DE NOTIFICACIONES")
print("=" * 80)

# Verificar notificaciones
notificaciones = Notification.objects.all().order_by('-created_at')
print(f"\n🔔 Total de notificaciones: {notificaciones.count()}")

if notificaciones.exists():
    print("\n🔍 Últimas 10 notificaciones:")
    for n in notificaciones[:10]:
        print(f"\n  ID: {n.id}")
        print(f"  Destinatario: {n.recipient.get_full_name() if n.recipient else 'Sin destinatario'}")
        print(f"  Username: {n.recipient.username if n.recipient else 'N/A'}")
        print(f"  Título: {n.title}")
        print(f"  Mensaje: {n.message[:100]}...")
        print(f"  Nivel: {n.level}")
        print(f"  Leída: {n.read}")
        print(f"  Fecha: {n.created_at}")
else:
    print("\n⚠️ NO HAY NOTIFICACIONES EN LA BASE DE DATOS")

print("\n" + "=" * 80)
print("VERIFICACIÓN DE HOGARES Y MADRES")
print("=" * 80)

hogares = HogarComunitario.objects.all()
print(f"\n🏠 Total de hogares: {hogares.count()}")

for h in hogares:
    print(f"\n  Hogar: {h.nombre_hogar}")
    if hasattr(h, 'madre') and h.madre:
        print(f"  ✓ Tiene madre: {h.madre.usuario.get_full_name()}")
        print(f"  ✓ Username: {h.madre.usuario.username}")
        print(f"  ✓ Email: {h.madre.usuario.correo}")
    else:
        print(f"  ⚠️ NO tiene madre asignada")

print("\n" + "=" * 80)
