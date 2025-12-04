import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from core.models import SolicitudMatriculacion

print("Actualizando solicitud ID 6 para simular primera corrección...")

sol = SolicitudMatriculacion.objects.get(id=6)
sol.intentos_correccion = 1
sol.save()

print(f"✅ Solicitud ID 6 actualizada")
print(f"   Intentos: {sol.intentos_correccion}/3")
print(f"   Restantes: {3 - sol.intentos_correccion}")
print(f"   Estado: {sol.estado}")
print(f"   Campos a corregir: {sol.campos_corregir}")
