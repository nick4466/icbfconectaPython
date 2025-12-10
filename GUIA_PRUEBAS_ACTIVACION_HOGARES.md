# 🧪 GUÍA DE PRUEBAS - Sistema de Activación de Hogares

## 📋 Pre-requisitos

Antes de comenzar las pruebas, asegúrate de que:
- ✅ El servidor de desarrollo está corriendo (`python manage.py runserver`)
- ✅ Tienes una cuenta de administrador activa
- ✅ La base de datos está migrada correctamente
- ✅ La configuración de email está lista (opcional para prueba completa)

---

## 🔄 PRUEBA 1: Creación de Hogar (Fase 1)

### Objetivo:
Verificar que el hogar se crea correctamente en estado `pendiente_visita` y que se programa la visita.

### Pasos:

1. **Iniciar sesión como administrador**
   ```
   URL: http://localhost:8000/login/
   Usuario: tu_documento_admin
   Contraseña: tu_contraseña
   ```

2. **Navegar a creación de agente educativo**
   ```
   Ruta: Dashboard → Agentes Educativos → "Crear Nuevo Agente"
   URL: http://localhost:8000/madres/crear/
   ```

3. **Completar Sección 1 - Datos Personales**
   - Tipo documento: Cédula de Ciudadanía
   - Número documento: 1234567890 (ficticio)
   - Nombres: María
   - Apellidos: Rodríguez
   - Correo: maria.rodriguez@test.com
   - Teléfono: 3001234567
   - Ciudad: Bogotá
   - Dirección: Calle 45 # 12-34

4. **Completar Sección 2 - Documentos**
   - Subir documentos requeridos (PDFs de prueba)
   - Cédula, certificado médico, certificado educación

5. **Completar Sección 3 - Información del Hogar**
   - Nombre del hogar: "Hogar Prueba 1"
   - Dirección: Carrera 30 # 50-60, Bogotá
   - Capacidad máxima: 14 niños
   - Número de convivientes: 2
   - Completar datos de convivientes

6. **Programar Primera Visita**
   - **IMPORTANTE**: Selecciona la fecha de **MAÑANA** (fecha de hoy + 1 día)
   - Debe ser un día laboral (lunes a viernes)
   - Verifica que aparezca el mensaje verde: "✅ Fecha válida: ..."

7. **Enviar Formulario**
   - Clic en "Guardar Agente Educativo"
   - Esperar mensaje de éxito

### ✅ Verificaciones:

- [ ] Mensaje de éxito muestra: "⚠️ El hogar permanecerá en estado 'Pendiente de Visita'"
- [ ] No hay errores en consola
- [ ] Redirección a lista de madres
- [ ] El hogar aparece en la lista

### 📝 Resultado Esperado:
```
✅ Hogar creado con estado: 'pendiente_visita'
✅ fecha_primera_visita: [fecha de mañana]
✅ Email enviado (si configurado)
✅ VisitaTecnica creada con estado 'agendada'
```

---

## 🎯 PRUEBA 2: Visualización del Botón de Activación

### Objetivo:
Verificar que el botón "Activar Hogar" aparece solo el día de la visita.

### Pasos:

1. **Navegar al Dashboard de Hogares**
   ```
   URL: http://localhost:8000/dashboard/admin/hogares/
   ```

2. **Verificar estado ANTES del día de la visita**
   - Buscar el hogar "Hogar Prueba 1"
   - Estado debe mostrar: "⏱ Pendiente"
   - **NO debe aparecer** el botón "Activar Hogar"
   - Solo deben verse: "Editar", "Visita", "Ver Carpeta"

3. **Simular el día de la visita**
   
   **Opción A - Avanzar fecha del sistema** (Temporal para pruebas):
   ```python
   # En Django Shell
   from datetime import date, timedelta
   from core.models import HogarComunitario
   
   hogar = HogarComunitario.objects.get(nombre_hogar="Hogar Prueba 1")
   hogar.fecha_primera_visita = date.today()  # Cambiar a HOY
   hogar.save()
   ```
   
   **Opción B - Esperar al día siguiente** (Recomendado para prueba real)

4. **Recargar el Dashboard**
   - Presionar F5 o Ctrl+R
   - Buscar nuevamente el hogar

### ✅ Verificaciones:

- [ ] Aparece botón verde "Activar Hogar"
- [ ] El botón tiene animación pulsante (brillo verde)
- [ ] El icono es un check-circle
- [ ] El botón está entre "Visita" y "Ver Carpeta"

### 📝 Resultado Esperado:
```html
<a href="/hogares/[id]/activar/" 
   class="btn btn-success btn-small" 
   style="animation: pulse-glow 2s infinite;">
  <i class="fas fa-check-circle"></i>
  Activar Hogar
</a>
```

---

## 📋 PRUEBA 3: Formulario de Activación

### Objetivo:
Verificar que el formulario de evaluación se muestra correctamente y solo el día de la visita.

### Pasos:

1. **Clic en el botón "Activar Hogar"**
   - Debe redireccionar a: `/hogares/[id]/activar/`

2. **Verificar Header del Formulario**
   - Título: "Evaluación de Primera Visita Técnica"
   - Información del hogar visible:
     - Nombre del hogar
     - Agente educativo
     - Dirección

3. **Revisar Secciones del Formulario**
   - [ ] **Tipo y Características de la Vivienda**
     - Tipo de vivienda (select)
     - Ubicación (select)
     - ¿Fuera de zonas de riesgo? (select)
   
   - [ ] **Servicios Públicos** (checkboxes)
     - Acueducto, Alcantarillado, Energía
     - Gas, Internet, Teléfono
   
   - [ ] **Espacios de la Vivienda** (checkboxes)
     - Sala, Comedor, Cocina, Patio
     - Espacio suficiente (select)
   
   - [ ] **Condiciones Generales** (selects)
     - Higiene, Orden, Estado de vivienda
   
   - [ ] **Condiciones Ambientales** (selects)
     - Ventilación, Iluminación
   
   - [ ] **Aspectos Familiares**
     - Acuerdo familiar (select)
     - Dinámica familiar (textarea)
   
   - [ ] **Observaciones y Conclusiones**
     - Observaciones generales (textarea)
     - Capacidad calculada (number)
     - Recomendación final (select con 4 opciones)

4. **Verificar Botones del Formulario**
   - [ ] Botón "Cancelar" (gris)
   - [ ] Botón "Guardar y Activar Hogar" (verde)

### ✅ Verificaciones de Validación:

**Intentar enviar formulario vacío:**
- [ ] No permite envío (campos required)
- [ ] Muestra mensajes de validación del navegador

**Intentar acceder en día incorrecto:**
```python
# Cambiar fecha_primera_visita a mañana
hogar.fecha_primera_visita = date.today() + timedelta(days=1)
hogar.save()

# Intentar acceder a /hogares/[id]/activar/
```
- [ ] Muestra mensaje de error: "El formulario solo está disponible el día programado"
- [ ] Redirecciona al dashboard

---

## ✅ PRUEBA 4: Activación Exitosa (Aprobado)

### Objetivo:
Completar el proceso de activación con recomendación "Aprobado".

### Pasos:

1. **Completar todos los campos del formulario**

   **Vivienda:**
   - Tipo: Casa
   - Ubicación: Urbana
   - Sin riesgo: Sí

   **Servicios:** (marcar todos)
   - ✓ Acueducto
   - ✓ Alcantarillado
   - ✓ Energía
   - ✓ Gas
   - ✓ Internet
   - ✓ Teléfono

   **Espacios:** (marcar todos)
   - ✓ Sala
   - ✓ Comedor
   - ✓ Cocina
   - ✓ Patio
   - Espacio suficiente: Sí

   **Condiciones:**
   - Higiene: Excelente
   - Orden: Bueno
   - Estado vivienda: Buen estado
   - Ventilación: Buena
   - Iluminación: Buena

   **Familia:**
   - Acuerdo: Sí, todos
   - Dinámica: "Familia nuclear bien constituida, buena comunicación"

   **Conclusiones:**
   - Observaciones: "Hogar cumple con todos los requisitos. Espacios amplios y bien iluminados."
   - Capacidad: 14
   - **Recomendación: Aprobado - Hogar APTO**

2. **Clic en "Guardar y Activar Hogar"**

### ✅ Verificaciones:

- [ ] Mensaje de éxito verde: "✅ ¡Hogar ACTIVADO exitosamente!"
- [ ] Redirección al dashboard
- [ ] Hogar ahora muestra estado "✓ Aprobado"
- [ ] **SI EMAIL CONFIGURADO**: Revisar bandeja del agente educativo
  - [ ] Email recibido con asunto "✅ Hogar Activado - ICBF Conecta"
  - [ ] Contiene credenciales de acceso
  - [ ] Contiene fecha de próxima visita

### 📝 Verificación en Base de Datos:

```python
# Django Shell
from core.models import HogarComunitario
from datetime import date

hogar = HogarComunitario.objects.get(nombre_hogar="Hogar Prueba 1")

print(f"Estado: {hogar.estado}")  # Esperado: 'activo'
print(f"Aptitud: {hogar.estado_aptitud}")  # Esperado: 'apto'
print(f"Última visita: {hogar.ultima_visita}")  # Esperado: fecha de hoy
print(f"Próxima visita: {hogar.proxima_visita}")  # Esperado: hoy + 365 días
print(f"Capacidad: {hogar.capacidad}")  # Esperado: 14
print(f"\nObservaciones:\n{hogar.observaciones_visita}")
```

**Resultado Esperado:**
```
Estado: activo
Aptitud: apto
Última visita: 2025-01-16
Próxima visita: 2026-01-16
Capacidad: 14

Observaciones:
=== EVALUACIÓN DE PRIMERA VISITA TÉCNICA ===
Fecha: 16/01/2025

VIVIENDA:
- Tipo: casa
- Ubicación: urbana
...
RECOMENDACIÓN: APROBADO
```

---

## ❌ PRUEBA 5: Activación No Aprobada

### Objetivo:
Verificar comportamiento cuando el hogar NO es aprobado.

### Pasos:

1. **Crear un segundo hogar de prueba**
   - Seguir PRUEBA 1 pero con datos diferentes
   - Nombre: "Hogar Prueba 2 - No Apto"

2. **Completar formulario de activación**
   - Marcar deficiencias (ejemplo):
     - Sin alcantarillado
     - Higiene: Regular
     - Ventilación: Mala
     - Espacio suficiente: No
   
   - **Recomendación: No Aprobado - NO APTO**

3. **Enviar formulario**

### ✅ Verificaciones:

- [ ] Mensaje de error rojo: "❌ Hogar NO APROBADO"
- [ ] Estado permanece "pendiente_visita"
- [ ] **NO** se envía email
- [ ] proxima_visita = null
- [ ] Observaciones guardadas con deficiencias

### 📝 Verificación en BD:

```python
hogar = HogarComunitario.objects.get(nombre_hogar="Hogar Prueba 2 - No Apto")

print(f"Estado: {hogar.estado}")  # Esperado: 'pendiente_visita'
print(f"Aptitud: {hogar.estado_aptitud}")  # Esperado: 'no_apto'
```

---

## 🔄 PRUEBA 6: Requiere Nueva Visita

### Objetivo:
Verificar que se puede solicitar reprogramación de visita.

### Pasos:

1. **Crear tercer hogar de prueba**
   - Nombre: "Hogar Prueba 3 - Nueva Visita"

2. **En formulario de activación seleccionar:**
   - **Recomendación: Requiere Nueva Visita**

3. **Enviar**

### ✅ Verificaciones:

- [ ] Mensaje info azul: "🔄 Se requiere NUEVA VISITA"
- [ ] `fecha_primera_visita = null` (permite reprogramar)
- [ ] Estado: 'pendiente_visita'
- [ ] Puede programar nueva visita desde dashboard

---

## 📊 PRUEBA 7: Validaciones de Seguridad

### Objetivo:
Intentar accesos no autorizados y fechas incorrectas.

### Escenarios a Probar:

#### 7.1 - Acceso sin login
```
1. Cerrar sesión
2. Intentar acceder a: /hogares/1/activar/
```
**Esperado**: Redirección a login

#### 7.2 - Acceso con rol incorrecto
```
1. Login como madre comunitaria
2. Intentar acceder a: /hogares/1/activar/
```
**Esperado**: Error 403 o redirección

#### 7.3 - Fecha incorrecta
```python
# Cambiar fecha_primera_visita a mañana
hogar.fecha_primera_visita = date.today() + timedelta(days=1)
hogar.save()

# Intentar acceder como admin
```
**Esperado**: Mensaje "El formulario solo está disponible el día programado"

#### 7.4 - Hogar ya activado
```python
# Activar hogar primero (PRUEBA 4)
# Luego intentar acceder nuevamente a /hogares/1/activar/
```
**Esperado**: Mensaje "Este hogar ya ha sido evaluado"

---

## 🎓 PRUEBA 8: Login del Agente Educativo

### Objetivo:
Verificar que el agente puede hacer login después de la activación.

### Pasos:

1. **Cerrar sesión de administrador**

2. **Intentar login con credenciales del agente**
   ```
   Usuario: 1234567890 (número de documento)
   Contraseña: 123456 (temporal)
   ```

3. **Verificar acceso**
   - [ ] Login exitoso
   - [ ] Redirección a dashboard de madre
   - [ ] Puede ver su hogar
   - [ ] Puede ver lista de niños (vacía inicialmente)

4. **Cambiar contraseña**
   - Ir a Perfil → Cambiar Contraseña
   - Cambiar de "123456" a contraseña segura

---

## 📈 PRUEBA 9: Cálculo de Próxima Visita

### Objetivo:
Verificar que la próxima visita se calcula correctamente (+365 días laborales).

### Pasos:

1. **Activar hogar en fecha específica**
   ```python
   # Ejemplo: Activación el 16 de enero de 2025 (jueves)
   fecha_activacion = date(2025, 1, 16)
   ```

2. **Verificar cálculo**
   ```python
   from core.views import calcular_proxima_visita
   
   proxima = calcular_proxima_visita(fecha_activacion)
   print(f"Activación: {fecha_activacion}")
   print(f"Próxima visita: {proxima}")
   print(f"Diferencia: {(proxima - fecha_activacion).days} días")
   print(f"Día semana: {proxima.strftime('%A')}")  # Debe ser laboral
   ```

### ✅ Verificaciones:

- [ ] Diferencia es 365 días (o más si ajustó por festivos/fin de semana)
- [ ] Día de la semana es lunes-viernes
- [ ] No cae en festivo colombiano

---

## 🔍 CHECKLIST FINAL

### Funcionalidad Completa:
- [ ] Creación de hogar en estado 'pendiente_visita'
- [ ] Programación de visita con validaciones de fecha
- [ ] Botón "Activar Hogar" solo visible el día correcto
- [ ] Animación pulsante del botón
- [ ] Formulario completo de evaluación
- [ ] Guardado de observaciones estructuradas
- [ ] Cambio de estado según recomendación
- [ ] Envío de email al activar (si configurado)
- [ ] Cálculo correcto de próxima visita (+365 días)
- [ ] Login exitoso del agente después de activación

### Validaciones de Seguridad:
- [ ] Solo administradores pueden activar
- [ ] Solo día exacto de visita permite activación
- [ ] No permite activación doble
- [ ] Protección contra accesos no autorizados

### Interfaz de Usuario:
- [ ] Diseño limpio y profesional
- [ ] Mensajes claros y descriptivos
- [ ] Feedback visual en tiempo real
- [ ] Navegación intuitiva

### Performance:
- [ ] Formularios cargan rápido
- [ ] Sin errores en consola
- [ ] Redirecciones correctas
- [ ] Email se envía sin bloquear UI (asíncrono)

---

## 🐛 REPORTE DE ERRORES

Si encuentras algún problema durante las pruebas, documéntalo así:

```
PRUEBA: [Número de prueba]
PASO: [Paso específico]
ERROR: [Descripción del error]
ESPERADO: [Comportamiento esperado]
OBTENIDO: [Comportamiento actual]
CONSOLA: [Errores en consola/logs]
SCREENSHOT: [Captura de pantalla si es visual]
```

---

## ✅ CONCLUSIÓN

Después de completar todas las pruebas:

1. **Si todas pasan** ✅:
   - El sistema está listo para producción
   - Documentar cualquier ajuste menor necesario
   - Preparar datos de demo para capacitación

2. **Si hay errores** ❌:
   - Documentar errores encontrados
   - Priorizar según criticidad
   - Corregir antes de deployment

---

**Fecha de Pruebas**: [Completar]  
**Testeado por**: [Completar]  
**Estado Final**: [ ] Aprobado / [ ] Requiere correcciones  
**Notas adicionales**: [Completar]
