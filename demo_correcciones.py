import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icbfconecta.settings')
django.setup()

from core.models import SolicitudMatriculacion

print("\n" + "="*70)
print("DEMOSTRACIÓN VISUAL DEL SISTEMA DE CORRECCIONES")
print("="*70)

sol = SolicitudMatriculacion.objects.get(id=6)

print(f"\n📋 SOLICITUD ID: {sol.id}")
print(f"📧 Email: {sol.email_acudiente}")
print(f"📊 Estado: {sol.estado.upper()}")

print("\n" + "─"*70)
print("CONTADOR DE INTENTOS:")
print("─"*70)

# Barra visual de intentos
intentos_usados = sol.intentos_correccion
intentos_restantes = 3 - intentos_usados

bar_usado = "█" * intentos_usados
bar_restante = "░" * intentos_restantes

print(f"\n  Usados:    [{bar_usado}{bar_restante}] {intentos_usados}/3")
print(f"  Restantes: [{bar_restante}{bar_usado}] {intentos_restantes}/3")

# Advertencias según intentos
if intentos_usados == 0:
    print("\n  ✅ Estado: Sin intentos de corrección")
elif intentos_usados == 1:
    print("\n  ⚠️  Estado: Primer intento usado - 2 intentos restantes")
elif intentos_usados == 2:
    print("\n  ⚠️⚠️ Estado: ADVERTENCIA - Solo 1 intento restante")
elif intentos_usados == 3:
    print("\n  🚫 Estado: LÍMITE ALCANZADO - No puede corregir más")
    print("  💡 Acción: Debe rechazar y solicitar nueva matriculación")

print("\n" + "─"*70)
print("CAMPOS MARCADOS PARA CORRECCIÓN:")
print("─"*70)

if sol.campos_corregir:
    for i, campo in enumerate(sol.campos_corregir, 1):
        # Traducir nombres técnicos a nombres legibles
        nombres_legibles = {
            'certificado_eps_nino': '🏥 Certificado EPS',
            'foto_nino': '📸 Foto del Niño',
            'carnet_vacunacion_nino': '💉 Carnet de Vacunación',
            'registro_civil_nino': '📄 Registro Civil',
            'documento_identidad_padre': '🪪 Documento Identidad Acudiente',
            'clasificacion_sisben_padre': '📋 Clasificación SISBEN',
            'nombres_nino': '👤 Nombres del Niño',
            'apellidos_nino': '👤 Apellidos del Niño',
        }
        
        nombre_mostrar = nombres_legibles.get(campo, f"📌 {campo}")
        print(f"  {i}. {nombre_mostrar}")
        print(f"     └─ Campo técnico: '{campo}'")
        print(f"     └─ Aparece en formulario con badge 'CORREGIR' 🟠")
else:
    print("  ℹ️  No hay campos marcados para corrección")

print("\n" + "─"*70)
print("VISTA PREVIA DEL EMAIL QUE RECIBIRÍA EL ACUDIENTE:")
print("─"*70)

print("""
┌──────────────────────────────────────────────────────────────┐
│  ✏️  CORRECCIONES REQUERIDAS                                 │
└──────────────────────────────────────────────────────────────┘

Tu solicitud de matriculación ha sido revisada y necesita 
algunas correcciones antes de ser aprobada.

┌─ 📋 Campos que requieren corrección: ────────────────────────┐
│""")

if sol.campos_corregir:
    for campo in sol.campos_corregir:
        nombres_legibles = {
            'certificado_eps_nino': 'Certificado EPS',
            'foto_nino': 'Foto del Niño',
            'carnet_vacunacion_nino': 'Carnet de Vacunación',
        }
        print(f"│  • {nombres_legibles.get(campo, campo)}")

print("""│
└───────────────────────────────────────────────────────────────┘

┌─ ⚠️  IMPORTANTE - Límite de Intentos: ───────────────────────┐
│                                                                │
│  Por favor, procure subir información correcta y legible.     │
│  Solo tiene 3 intentos para corregir la información de la     │
│  matrícula.                                                   │
│                                                                │""")

print(f"│  Intentos usados:     {intentos_usados} de 3                                   │")
print(f"│  Intentos restantes:  {intentos_restantes}                                       │")

print("""│                                                                │
│  Si excede los 3 intentos, deberá solicitar la matrícula      │
│  nuevamente desde el inicio.                                  │
│                                                                │
└───────────────────────────────────────────────────────────────┘

        [ 🔗 Corregir Formulario ]

""")

print("─"*70)
print("VISTA DEL FORMULARIO PÚBLICO (cuando acudiente abre el link):")
print("─"*70)

print("""
┌──────────────────────────────────────────────────────────────┐
│  📄 Documentos Requeridos                                     │
└──────────────────────────────────────────────────────────────┘
""")

if sol.campos_corregir:
    for campo in sol.campos_corregir:
        if 'eps' in campo.lower():
            print("""
  ┌────────────────────────────────────────────────────┐
  │ Certificado EPS *  🟠 CORREGIR                     │
  │                                                    │
  │  ╔═══════════════════════════════════════════╗    │
  │  ║  🏥                                       ║    │ <- RESALTADO NARANJA
  │  ║  Cambiar certificado                      ║    │ <- CON ANIMACIÓN
  │  ║  (JPG, PNG, PDF - Máx 5MB)                ║    │
  │  ╚═══════════════════════════════════════════╝    │
  │                                                    │
  │  ✓ Certificado actual cargado                     │
  │    Puedes cambiarlo seleccionando uno nuevo       │
  └────────────────────────────────────────────────────┘
""")

print("\n" + "="*70)
print("FIN DE LA DEMOSTRACIÓN")
print("="*70 + "\n")
