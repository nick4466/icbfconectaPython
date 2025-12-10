"""
Script para migrar datos de capacidad_calculada a capacidad en hogares existentes.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from core.models import HogarComunitario

def migrar_capacidades():
    """
    Migra los valores de capacidad_calculada al nuevo campo capacidad.
    """
    print("🔍 Migrando capacidades de hogares...\n")
    
    hogares = HogarComunitario.objects.all()
    
    migrados = 0
    sin_capacidad = 0
    
    for hogar in hogares:
        if hogar.capacidad_calculada and not hogar.capacidad:
            hogar.capacidad = hogar.capacidad_calculada
            hogar.save()
            print(f"   ✅ {hogar.nombre_hogar}: capacidad = {hogar.capacidad}")
            migrados += 1
        elif not hogar.capacidad and not hogar.capacidad_calculada:
            # Hogares sin capacidad asignada (probablemente aún no tienen visita)
            print(f"   ⚠️ {hogar.nombre_hogar}: Sin capacidad asignada (pendiente de visita)")
            sin_capacidad += 1
        elif hogar.capacidad:
            print(f"   ℹ️ {hogar.nombre_hogar}: Ya tiene capacidad = {hogar.capacidad}")
    
    print(f"\n📊 Resumen:")
    print(f"   ✅ Migrados: {migrados}")
    print(f"   ⚠️ Sin capacidad: {sin_capacidad}")
    print(f"   ℹ️ Ya tenían capacidad: {hogares.count() - migrados - sin_capacidad}")
    print(f"\n✅ Migración completada")


if __name__ == '__main__':
    migrar_capacidades()
