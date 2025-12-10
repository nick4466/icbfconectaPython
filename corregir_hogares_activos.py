"""
Script para corregir hogares activos que no tienen ultima_visita registrada
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from core.models import HogarComunitario
from datetime import date

print("=" * 80)
print("CORRECCIÓN DE HOGARES ACTIVOS SIN VISITA REGISTRADA")
print("=" * 80)

# Buscar hogares activos sin ultima_visita
hogares_sin_visita = HogarComunitario.objects.filter(
    estado='activo',
    ultima_visita__isnull=True
)

print(f"\n📊 Hogares activos sin visita registrada: {hogares_sin_visita.count()}")

if hogares_sin_visita.exists():
    print("\n🔧 Corrigiendo...")
    for hogar in hogares_sin_visita:
        # Si tiene fecha_primera_visita, usarla
        if hogar.fecha_primera_visita:
            hogar.ultima_visita = hogar.fecha_primera_visita
        else:
            # Si no, usar la fecha de registro
            hogar.ultima_visita = hogar.fecha_registro if hasattr(hogar, 'fecha_registro') else date.today()
            hogar.fecha_primera_visita = hogar.ultima_visita
        
        hogar.save()
        print(f"   ✅ {hogar.nombre_hogar}: ultima_visita = {hogar.ultima_visita}")
    
    print(f"\n✅ {hogares_sin_visita.count()} hogares corregidos")
else:
    print("\n✅ Todos los hogares activos tienen visita registrada")

print("\n" + "=" * 80)
