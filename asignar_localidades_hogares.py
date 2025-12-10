"""
Script para asignar localidades a hogares creados antes de implementar el sistema de localidades.
Asigna localidades de Bogotá a los 3 hogares existentes.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from core.models import HogarComunitario, LocalidadBogota

def asignar_localidades():
    """
    Asigna localidades de Bogotá a los hogares sin localidad asignada.
    """
    print("🔍 Buscando hogares sin localidad asignada...")
    
    hogares_sin_localidad = HogarComunitario.objects.filter(localidad_bogota__isnull=True)
    
    if not hogares_sin_localidad.exists():
        print("✅ Todos los hogares ya tienen localidad asignada.")
        return
    
    print(f"📊 Hogares sin localidad: {hogares_sin_localidad.count()}\n")
    
    # Asignaciones basadas en las direcciones aproximadas
    # Puedes modificar estas asignaciones según sea necesario
    asignaciones = {
        'niños felices': 'Usaquén',          # Localidad 1
        'niñosfeliz2': 'Chapinero',          # Localidad 2  
        'bolivar city': 'Santa Fe',          # Localidad 3
        'Los pinochitos': 'San Cristóbal',   # Localidad 4
    }
    
    print("🔧 Asignando localidades...\n")
    
    for hogar in hogares_sin_localidad:
        nombre_normalizado = hogar.nombre_hogar.lower().strip()
        
        # Buscar en las asignaciones
        localidad_nombre = None
        for nombre_hogar, loc_nombre in asignaciones.items():
            if nombre_hogar.lower() in nombre_normalizado or nombre_normalizado in nombre_hogar.lower():
                localidad_nombre = loc_nombre
                break
        
        # Si no se encuentra, asignar Usaquén por defecto
        if not localidad_nombre:
            localidad_nombre = 'Usaquén'
            print(f"   ⚠️ '{hogar.nombre_hogar}' no encontrado en asignaciones, usando Usaquén por defecto")
        
        try:
            localidad = LocalidadBogota.objects.get(nombre=localidad_nombre)
            hogar.localidad_bogota = localidad
            
            # También actualizar el campo localidad (texto) para compatibilidad
            hogar.localidad = localidad_nombre
            
            hogar.save()
            
            print(f"   ✅ {hogar.nombre_hogar}: {localidad}")
            
        except LocalidadBogota.DoesNotExist:
            print(f"   ❌ Error: Localidad '{localidad_nombre}' no existe en la base de datos")
            print(f"      Hogar '{hogar.nombre_hogar}' no actualizado")
    
    print(f"\n✅ Proceso completado")
    
    # Verificar resultado
    print("\n📋 Estado actual de los hogares:")
    for hogar in HogarComunitario.objects.all():
        localidad = hogar.localidad_bogota.nombre if hogar.localidad_bogota else "SIN LOCALIDAD"
        ciudad = hogar.ciudad.nombre if hogar.ciudad else "SIN CIUDAD"
        print(f"   • {hogar.nombre_hogar}: {ciudad} - {localidad}")


if __name__ == '__main__':
    asignar_localidades()
