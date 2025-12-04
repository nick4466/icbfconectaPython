#!/usr/bin/env python
"""Script para verificar notificaciones en detalle"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from notifications.models import Notification

print("=" * 80)
print("VERIFICACIÓN DETALLADA DE NOTIFICACIONES")
print("=" * 80)

notificaciones = Notification.objects.filter(title__contains='Solicitud de Matrícula').order_by('-created_at')

print(f"\n🔔 Total de notificaciones de matrícula: {notificaciones.count()}\n")

for n in notificaciones:
    print(f"Notificación ID: {n.id}")
    print(f"  Título: {n.title}")
    print(f"  Mensaje: {n.message[:100]}")
    print(f"  Recipient (objeto): {n.recipient}")
    print(f"  Recipient ID: {n.recipient.id if n.recipient else 'None'}")
    print(f"  Recipient type: {type(n.recipient)}")
    
    if n.recipient:
        print(f"  Usuario documento: {n.recipient.documento}")
        print(f"  Usuario nombres: {n.recipient.nombres}")
        print(f"  Usuario apellidos: {n.recipient.apellidos}")
        print(f"  Usuario correo: {n.recipient.correo}")
        print(f"  get_full_name(): '{n.recipient.get_full_name()}'")
        print(f"  __str__(): '{str(n.recipient)}'")
    else:
        print(f"  ⚠️ RECIPIENT ES NONE")
    
    print(f"  Leída: {n.read}")
    print(f"  Fecha: {n.created_at}")
    print()

print("=" * 80)
