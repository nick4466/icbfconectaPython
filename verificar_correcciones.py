import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from core.models import SolicitudMatriculacion

print("=" * 60)
print("VERIFICACIÓN DEL SISTEMA DE CORRECCIONES")
print("=" * 60)

solicitudes = SolicitudMatriculacion.objects.all()

print(f"\n📊 Total de solicitudes: {solicitudes.count()}")

for sol in solicitudes:
    print(f"\n{'='*50}")
    print(f"ID: {sol.id}")
    print(f"Email: {sol.email_acudiente}")
    print(f"Estado: {sol.estado}")
    print(f"Intentos de corrección: {sol.intentos_correccion}/3")
    print(f"Intentos restantes: {3 - sol.intentos_correccion}")
    
    if sol.campos_corregir:
        print(f"Campos a corregir ({len(sol.campos_corregir)}):")
        for campo in sol.campos_corregir:
            print(f"  - {campo}")
    else:
        print("Campos a corregir: Ninguno")

print("\n" + "=" * 60)
print("VERIFICACIÓN COMPLETA")
print("=" * 60)
