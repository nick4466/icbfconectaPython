# 🆕 NUEVA FUNCIONALIDAD: SOLICITUD DE MATRÍCULA INICIADA POR PADRE

## 📋 Descripción General

Esta funcionalidad permite a los padres/tutores **iniciar solicitudes de matrícula** directamente desde su dashboard, invirtiendo el flujo tradicional donde la madre comunitaria envía la invitación.

---

## 🔄 Flujo Completo

### **Paso 1: Padre Inicia Solicitud**

**URL:** `/padre/solicitar-matricula/`  
**Vista:** `padre_solicitar_matricula()`

El padre accede a un formulario donde:
1. Selecciona un hogar comunitario
2. Ingresa datos básicos del niño:
   - Nombres
   - Apellidos  
   - Fecha de nacimiento
   - Género

**Proceso Backend:**
```python
- Crea SolicitudMatriculacion con tipo_solicitud='solicitud_padre'
- Asigna padre_solicitante = perfil del padre actual
- Pre-llena datos del padre desde su usuario
- Estado inicial: 'pendiente'
```

---

### **Paso 2: Validación Automática de Cupos**

```python
def validar_cupos_disponibles(self):
    capacidad_total = hogar.capacidad_calculada
    ninos_activos = Nino.objects.filter(hogar=hogar, estado='activo').count()
    cupos_disponibles = capacidad_total - ninos_activos
    
    self.cupos_validados = True
    self.tiene_cupos_disponibles = (cupos_disponibles > 0)
    self.save()
```

---

### **Paso 3A: Hay Cupos Disponibles ✅**

**Notificación a la Madre:**
- Email automático con información básica del niño y padre
- Badge verde: "Cupos disponibles"

**Opciones de la Madre en Panel de Revisión:**

#### **Opción 1: Enviar Formulario Completo**
```
URL: /solicitudes/enviar-formulario/
Vista: enviar_formulario_a_padre()
```

**Proceso:**
- Renueva el token de la solicitud
- Establece nueva fecha de expiración (48 horas)
- Envía email al padre con enlace al formulario completo

**Email al Padre:** "Formulario de Matrícula - Tu solicitud fue pre-aprobada"

#### **Opción 2: Rechazar**
(Mismo proceso que solicitudes normales)

---

### **Paso 3B: Sin Cupos ❌**

**Notificación a la Madre:**
- Email automático con alerta de "Sin cupos"
- Badge amarillo: "Sin cupos disponibles"

**Opciones de la Madre:**
- Solo puede **rechazar** la solicitud
- Motivo automático: "No hay cupos disponibles"

---

### **Paso 4: Padre Llena Formulario Reducido**

**URL:** `/matricula/publico/<token>/`  
**Vista:** `formulario_matricula_publico(token)`

**Detección del Tipo:**
```python
es_solicitud_padre = (solicitud.tipo_solicitud == 'solicitud_padre')
```

**Template Context:**
```python
{
    'mostrar_solo_nino': True,  # Oculta sección de datos del padre
    'es_solicitud_padre': True,
    ...
}
```

**Formulario Reducido Muestra Solo:**
- ✅ Datos completos del niño (documento, tipo sangre, discapacidades, etc.)
- ✅ Documentos del niño (foto, carnet vacunación, EPS, registro civil)
- ❌ Datos del padre (ya están pre-llenados)
- ❌ Contraseña del padre (ya existe)

---

### **Paso 5: Madre Revisa y Aprueba**

**URL:** `/solicitudes/aprobar/`  
**Vista:** `aprobar_solicitud_matricula()`

**Lógica Diferenciada:**

```python
if solicitud.tipo_solicitud == 'solicitud_padre':
    # SALTAR creación de padre - ya existe
    padre = solicitud.padre_solicitante
    
else:
    # LÓGICA ORIGINAL: crear o buscar padre
    # ... código existente ...
```

**Resultado:**
- ✅ Niño creado y matriculado
- ✅ Asociado al padre_solicitante
- ✅ Estado → 'aprobado' → 'token_usado'

---

## 🗃️ Cambios en el Modelo

### **Nuevos Campos en `SolicitudMatriculacion`:**

```python
tipo_solicitud = models.CharField(
    max_length=30,
    choices=[
        ('invitacion_madre', 'Invitación de Madre Comunitaria'),
        ('solicitud_padre', 'Solicitud Iniciada por Padre/Tutor'),
    ],
    default='invitacion_madre'
)

padre_solicitante = models.ForeignKey(
    'Padre',
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='solicitudes_matricula'
)

cupos_validados = models.BooleanField(default=False)
tiene_cupos_disponibles = models.BooleanField(default=False)
```

**Migración:** `0043_solicitudmatriculacion_cupos_validados_and_more.py`

---

## 🔗 Nuevas URLs

```python
# Para padres
path('padre/solicitar-matricula/', views.padre_solicitar_matricula, 
     name='padre_solicitar_matricula'),

# Para madres
path('solicitudes/enviar-formulario/', views.enviar_formulario_a_padre, 
     name='enviar_formulario_a_padre'),
```

---

## 📧 Nuevos Emails

### **1. `nueva_solicitud_padre.html`**
- Destinatario: Madre comunitaria
- Disparador: Cuando padre envía solicitud
- Contenido: Datos básicos niño + padre + estado de cupos

### **2. `formulario_solicitud_padre.html`**
- Destinatario: Padre/tutor
- Disparador: Cuando madre envía formulario completo
- Contenido: Link al formulario + información del hogar

---

## 🎨 Nuevo Template

### **`templates/padre/solicitar_matricula.html`**

**Características:**
- Lista de hogares comunitarios disponibles
- Formulario de datos básicos del niño
- Validación frontend
- Integración con SweetAlert2
- Responsive design

---

## ⚙️ Adaptaciones a Código Existente

### **1. `formulario_matricula_publico()`**
```python
# GET: Detectar tipo de solicitud
es_solicitud_padre = solicitud.tipo_solicitud == 'solicitud_padre'

context = {
    'mostrar_solo_nino': es_solicitud_padre,
    ...
}
```

### **2. `aprobar_solicitud_matricula()`**
```python
if solicitud.tipo_solicitud == 'solicitud_padre':
    padre = solicitud.padre_solicitante  # Ya existe
else:
    # Lógica original de crear/buscar padre
    ...
```

### **3. `listar_solicitudes_matricula()`**
```python
# Agregar campos al JSON
datos.append({
    ...
    'tipo_solicitud': s.tipo_solicitud,
    'cupos_validados': s.cupos_validados,
    'tiene_cupos_disponibles': s.tiene_cupos_disponibles,
    'padre_solicitante': s.padre_solicitante.usuario.get_full_name() if s.padre_solicitante else None,
})
```

### **4. `detalle_solicitud_matricula()`**
```python
datos = {
    ...
    'tipo_solicitud': solicitud.tipo_solicitud,
    'padre_solicitante': {
        'nombres': solicitud.padre_solicitante.usuario.nombres,
        ...
    } if solicitud.padre_solicitante else None,
}
```

---

## 📊 Diagrama de Estados

```
SOLICITUD INICIADA POR PADRE:
┌─────────────────────────────────────┐
│  Padre crea solicitud               │
│  tipo_solicitud='solicitud_padre'   │
│  Estado: PENDIENTE                  │
└──────────┬──────────────────────────┘
           │
    ┌──────┴───────┐
    │ Valida Cupos │
    └──────┬───────┘
           │
    ┌──────┴──────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌──────────┐
│ CUPOS ✅│      │NO CUPOS ❌│
└────┬────┘      └────┬─────┘
     │                │
     │    ┌───────────┘
     │    │
     ▼    ▼
┌──────────────────┐
│ Madre Revisa     │
└────┬─────────────┘
     │
     ├─► ENVIAR FORMULARIO ──► Padre llena ──► REVISIÓN ──► APROBADO
     │                                             │
     │                                             └─► CORRECCIÓN (max 3)
     │                                             │
     │                                             └─► RECHAZADO
     │
     └─► RECHAZAR DIRECTAMENTE ──► RECHAZADO
```

---

## 🆚 Comparación: Invitación vs Solicitud

| Aspecto | Invitación Madre | Solicitud Padre |
|---------|------------------|-----------------|
| **Quién inicia** | Madre comunitaria | Padre/tutor |
| **Datos iniciales** | Solo email | Email + datos básicos niño |
| **Validación cupos** | No | Sí (automática) |
| **Datos del padre en formulario** | Todos | Solo heredados (no editable) |
| **Contraseña padre** | Padre crea | Ya existe |
| **Flujo aprobación** | Crear padre → Crear niño | Solo crear niño |
| **Email inicial** | Invitación genérica | Solicitud específica |

---

## ✅ Ventajas de la Nueva Funcionalidad

1. **Empodera a los Padres:** Pueden iniciar el proceso sin esperar invitación
2. **Validación Temprana:** Se verifica cupos antes de llenar formulario completo
3. **Menos Duplicación:** Datos del padre se heredan automáticamente
4. **Transparencia:** Padre sabe de inmediato si hay cupos
5. **Eficiencia:** Madre solo revisa solicitudes viables
6. **Reutilización:** Usa toda la infraestructura existente

---

## 🧪 Casos de Prueba

### **Escenario 1: Con Cupos Disponibles**
1. Padre solicita matrícula
2. Sistema valida: 3 cupos disponibles
3. Madre recibe email verde
4. Madre envía formulario
5. Padre llena solo datos del niño
6. Madre aprueba
7. Niño matriculado ✅

### **Escenario 2: Sin Cupos**
1. Padre solicita matrícula
2. Sistema valida: 0 cupos
3. Madre recibe email amarillo
4. Madre rechaza (única opción)
5. Padre recibe email de rechazo
6. Fin del proceso ❌

### **Escenario 3: Correcciones**
1. Flujo normal hasta formulario
2. Padre llena formulario
3. Madre solicita corrección (foto borrosa)
4. Padre corrige
5. Madre aprueba
6. Niño matriculado ✅

---

## 📝 Notas de Implementación

- ✅ Backward compatible con solicitudes existentes
- ✅ No rompe flujo de invitaciones tradicional
- ✅ Migración ejecutada exitosamente
- ✅ Todos los templates creados
- ✅ URLs configuradas
- ✅ Emails de notificación implementados

---

## 🚀 Próximos Pasos (Opcional)

1. **Dashboard del Padre:**
   - Agregar botón "Solicitar Matrícula para Nuevo Niño"
   - Mostrar estado de solicitudes pendientes

2. **Panel de Madre:**
   - Badge diferenciador para solicitudes de padre
   - Filtro por tipo de solicitud
   - Vista previa de cupos antes de enviar formulario

3. **Métricas:**
   - Tasa de aprobación por tipo de solicitud
   - Tiempo promedio de respuesta
   - Conversión solicitud → matrícula

---

## 📞 Soporte

Para cualquier duda sobre esta funcionalidad, consultar el código en:
- **Modelo:** `core/models.py` (líneas 580-750)
- **Vistas:** `core/views.py` (líneas 2650-3350)
- **URLs:** `icbfconecta/urls.py` (líneas 140-160)
- **Templates:** `templates/padre/solicitar_matricula.html`
- **Emails:** `templates/emails/nueva_solicitud_padre.html` y `formulario_solicitud_padre.html`

---

**Fecha de Implementación:** 11 de diciembre de 2025  
**Versión:** 1.0  
**Estado:** ✅ COMPLETADO
