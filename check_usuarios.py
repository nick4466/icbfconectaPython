#!/usr/bin/env python
"""Script para verificar usuarios y madres"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from core.models import Usuario, MadreComunitaria, HogarComunitario

print("=" * 80)
print("VERIFICACIÓN DETALLADA DE USUARIOS Y MADRES")
print("=" * 80)

# Verificar madres
madres = MadreComunitaria.objects.all()
print(f"\n👩 Total de madres comunitarias: {madres.count()}\n")

for madre in madres:
    print(f"Madre ID: {madre.id}")
    print(f"  Usuario asociado: {madre.usuario}")
    print(f"  Usuario ID: {madre.usuario.id if madre.usuario else 'None'}")
    print(f"  Usuario username: {madre.usuario.username if madre.usuario else 'None'}")
    print(f"  Usuario nombres: {madre.usuario.nombres if madre.usuario else 'None'}")
    print(f"  Usuario apellidos: {madre.usuario.apellidos if madre.usuario else 'None'}")
    print(f"  Usuario correo: {madre.usuario.correo if madre.usuario else 'None'}")
    print(f"  Usuario rol: {madre.usuario.rol.nombre_rol if madre.usuario and madre.usuario.rol else 'None'}")
    
    # Verificar hogares de esta madre
    hogares = HogarComunitario.objects.filter(madre=madre)
    print(f"  Hogares asignados: {hogares.count()}")
    for hogar in hogares:
        print(f"    - {hogar.nombre_hogar} (ID: {hogar.id})")
    print()

print("\n" + "=" * 80)
print("VERIFICACIÓN DE RELACIÓN HOGAR -> MADRE -> USUARIO")
print("=" * 80)

hogares = HogarComunitario.objects.all()
for hogar in hogares:
    print(f"\n🏠 Hogar: {hogar.nombre_hogar} (ID: {hogar.id})")
    print(f"  ├─ Madre: {hogar.madre}")
    if hogar.madre:
        print(f"  ├─ Madre ID: {hogar.madre.id}")
        print(f"  ├─ Usuario: {hogar.madre.usuario}")
        if hogar.madre.usuario:
            print(f"  ├─ Usuario ID: {hogar.madre.usuario.id}")
            print(f"  ├─ Username: {hogar.madre.usuario.username}")
            print(f"  ├─ Email: {hogar.madre.usuario.correo}")
            print(f"  ├─ Nombres: '{hogar.madre.usuario.nombres}'")
            print(f"  ├─ Apellidos: '{hogar.madre.usuario.apellidos}'")
            print(f"  └─ get_full_name(): '{hogar.madre.usuario.get_full_name()}'")
        else:
            print(f"  └─ ⚠️ USUARIO ES NONE")
    else:
        print(f"  └─ ⚠️ MADRE ES NONE")

print("\n" + "=" * 80)
