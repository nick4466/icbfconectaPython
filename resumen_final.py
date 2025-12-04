#!/usr/bin/env python
"""Script de resumen final del sistema de notificaciones"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from core.models import SolicitudMatriculacion, HogarComunitario, Usuario
from notifications.models import Notification

print("\n" + "="*80)
print("RESUMEN FINAL DEL SISTEMA DE NOTIFICACIONES DE MATRÍCULA")
print("="*80)

# 1. Verificar solicitudes
solicitudes = SolicitudMatriculacion.objects.all().order_by('-fecha_creacion')[:5]
print(f"\n✅ SOLICITUDES GUARDADAS: {SolicitudMatriculacion.objects.count()} total")
print(f"\nÚltimas 5 solicitudes:")
for s in solicitudes:
    print(f"  • ID {s.id}: {s.nombres_nino or '[Sin nombre]'} {s.apellidos_nino or ''}")
    print(f"    Email: {s.email_acudiente}")
    print(f"    Hogar: {s.hogar.nombre_hogar}")
    print(f"    Estado: {s.estado}")
    print()

# 2. Verificar notificaciones
notifs_matricula = Notification.objects.filter(
    title__contains='Solicitud de Matrícula'
).order_by('-created_at')[:5]

print(f"\n✅ NOTIFICACIONES CREADAS: {Notification.objects.filter(title__contains='Solicitud').count()} total")
print(f"\nÚltimas 5 notificaciones de matrícula:")
for n in notifs_matricula:
    print(f"  • ID {n.id}: {n.title}")
    if n.recipient:
        print(f"    Para: {n.recipient.nombres} {n.recipient.apellidos}")
        print(f"    Email: {n.recipient.correo}")
        print(f"    Leída: {'✓ Sí' if n.read else '✗ No'}")
    else:
        print(f"    ⚠️ Sin destinatario")
    print()

# 3. Verificar hogares y madres
hogares = HogarComunitario.objects.all()
print(f"\n✅ HOGARES CONFIGURADOS: {hogares.count()} total")
for h in hogares:
    print(f"\n  🏠 {h.nombre_hogar}")
    if h.madre and h.madre.usuario:
        user = h.madre.usuario
        print(f"    Madre: {user.nombres} {user.apellidos}")
        print(f"    Email: {user.correo}")
        
        # Contar notificaciones no leídas de esta madre
        unread = Notification.objects.filter(recipient=user, read=False).count()
        print(f"    Notificaciones no leídas: {unread}")
    else:
        print(f"    ⚠️ Sin madre asignada")

print("\n" + "="*80)
print("ESTADO DEL SISTEMA")
print("="*80)

# Verificar usuarios madre
madres_users = Usuario.objects.filter(rol__nombre_rol='madre_comunitaria')
print(f"\n✅ Usuarios madre comunitaria: {madres_users.count()}")
for m in madres_users:
    notifs_count = Notification.objects.filter(recipient=m, read=False).count()
    print(f"  • {m.nombres} {m.apellidos} ({m.correo})")
    print(f"    Notificaciones pendientes: {notifs_count}")

print("\n" + "="*80)
print("DIAGNÓSTICO")
print("="*80)

# Diagnóstico
problemas = []

if not solicitudes.exists():
    problemas.append("❌ No hay solicitudes en la base de datos")

if not notifs_matricula.exists():
    problemas.append("❌ No hay notificaciones de matrícula creadas")

for h in hogares:
    if not (h.madre and h.madre.usuario):
        problemas.append(f"❌ El hogar '{h.nombre_hogar}' no tiene madre asignada")

if problemas:
    print("\n⚠️ PROBLEMAS DETECTADOS:")
    for p in problemas:
        print(f"  {p}")
else:
    print("\n✅ ¡TODO ESTÁ FUNCIONANDO CORRECTAMENTE!")
    print("\nPara ver las notificaciones:")
    print("  1. Inicia sesión como madre comunitaria")
    print("  2. Busca el ícono de campana (🔔) en la barra de navegación")
    print("  3. Verás un número rojo con las notificaciones pendientes")
    print("  4. Haz clic para ver el menú desplegable de notificaciones")

print("\n" + "="*80 + "\n")
