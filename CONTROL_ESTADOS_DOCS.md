# 🔄 Sistema de Control de Estados - Solicitudes de Matriculación

## Estados Disponibles

El sistema maneja **7 estados** diferentes para el ciclo de vida completo de una solicitud:

### 1️⃣ **pendiente** (Estado Inicial)
- **Descripción**: Solicitud creada pero aún no revisada por la madre comunitaria
- **Color**: Amarillo (`#fff3cd`)
- **Icono**: ⏳
- **Acciones disponibles**:
  - Acudiente puede completar/editar formulario
  - Acudiente puede cancelar solicitud
  - Madre puede aprobar, rechazar o devolver para corrección
- **Transiciones posibles**: → `aprobado`, `rechazado`, `correccion`, `cancelado_usuario`, `cancelado_expiracion`

### 2️⃣ **correccion** (En Corrección)
- **Descripción**: Solicitud devuelta para que el acudiente corrija campos específicos
- **Color**: Naranja claro (`#ffe5b4`)
- **Icono**: ✏️
- **Límite**: Máximo 3 intentos de corrección
- **Acciones disponibles**:
  - Acudiente puede editar SOLO campos marcados para corrección
  - Acudiente puede cancelar solicitud
  - Madre puede aprobar o rechazar después de corrección
- **Transiciones posibles**: → `aprobado`, `rechazado`, `cancelado_usuario`, `limite_excedido`

### 3️⃣ **aprobado** (Aprobado)
- **Descripción**: Solicitud aprobada y niño matriculado exitosamente
- **Color**: Verde (`#d4edda`)
- **Icono**: ✅
- **Acciones disponibles**:
  - Ver historial de cambios
  - Token se marca automáticamente como `token_usado`
- **Transiciones posibles**: → `token_usado` (automático)
- **Estado final**: SÍ (no se puede modificar)

### 4️⃣ **rechazado** (Rechazado)
- **Descripción**: Solicitud rechazada por la madre comunitaria con motivo
- **Color**: Rojo claro (`#f8d7da`)
- **Icono**: ❌
- **Campos relacionados**:
  - `motivo_rechazo`: Razón del rechazo
  - `fecha_rechazo`: Timestamp del rechazo
- **Acciones disponibles**:
  - Ver motivo de rechazo
  - Eliminar solicitud (después de X días configurable)
- **Estado final**: SÍ (no se puede modificar)

### 5️⃣ **cancelado_expiracion** (Cancelado por Expiración)
- **Descripción**: Token expirado automáticamente por el sistema
- **Color**: Naranja (`#ffe0b2`)
- **Icono**: ⏰
- **Proceso automático**:
  - Ejecutado por scheduler diario (9:00 AM)
  - Cancela solicitudes pendientes/corrección con `fecha_expiracion < ahora`
- **Campos relacionados**:
  - `fecha_cancelacion`: Timestamp de cancelación
  - `motivo_cancelacion`: Generado automáticamente con fecha de expiración
- **Estado final**: SÍ (archivos se limpian automáticamente)

### 6️⃣ **cancelado_usuario** (Cancelado por Usuario)
- **Descripción**: Acudiente canceló voluntariamente su solicitud
- **Color**: Gris (`#e9ecef`)
- **Icono**: 🚫
- **Proceso**:
  - Botón "Cancelar Solicitud" en formulario público
  - Requiere confirmación con SweetAlert
  - Motivo opcional ingresado por el usuario
- **Campos relacionados**:
  - `fecha_cancelacion`: Timestamp de cancelación
  - `motivo_cancelacion`: Razón proporcionada por el usuario
- **Notificaciones**: Envía notificación a madre comunitaria
- **Estado final**: SÍ

### 7️⃣ **token_usado** (Token Usado)
- **Descripción**: Token ya utilizado para matricular un niño
- **Color**: Azul claro (`#cce5ff`)
- **Icono**: 🔒
- **Proceso automático**:
  - Se marca automáticamente después de aprobar solicitud
  - Previene reenvíos o intentos de reutilización del enlace
- **Objetivo**: Seguridad - evitar duplicados
- **Estado final**: SÍ

---

## Diagrama de Flujo de Estados

```
┌─────────────┐
│  PENDIENTE  │ (Inicio)
└──────┬──────┘
       │
       ├──────────────────┬──────────────────┬───────────────────┬──────────────────┐
       │                  │                  │                   │                  │
       v                  v                  v                   v                  v
┌─────────────┐    ┌─────────────┐   ┌──────────────┐   ┌─────────────┐   ┌────────────────┐
│  CORRECCION │    │  APROBADO   │   │  RECHAZADO   │   │  CANCELADO  │   │   CANCELADO    │
│             │    │             │   │              │   │   USUARIO   │   │  EXPIRACION    │
└──────┬──────┘    └──────┬──────┘   └──────────────┘   └─────────────┘   └────────────────┘
       │                  │                 ▲
       │                  v                 │
       │           ┌─────────────┐          │
       ├──────────>│ TOKEN USADO │          │
       │           └─────────────┘          │
       │                                    │
       └────────────────────────────────────┘
```

---

## Estados Terminales vs. Activos

### ✅ Estados Activos (Se puede interactuar)
- `pendiente`
- `correccion`

### 🔒 Estados Terminales (No se puede modificar)
- `aprobado`
- `rechazado`
- `cancelado_expiracion`
- `cancelado_usuario`
- `token_usado`

---

## Validaciones por Estado

### Al acceder al formulario público:

| Estado | ¿Puede ver formulario? | ¿Puede editar? | ¿Puede cancelar? |
|--------|------------------------|----------------|------------------|
| `pendiente` | ✅ Sí | ✅ Todos los campos | ✅ Sí |
| `correccion` | ✅ Sí | ⚠️ Solo campos marcados | ✅ Sí |
| `aprobado` | ❌ Bloqueado | ❌ No | ❌ No |
| `token_usado` | ❌ Bloqueado | ❌ No | ❌ No |
| `rechazado` | ❌ Bloqueado | ❌ No | ❌ No |
| `cancelado_expiracion` | ❌ Bloqueado | ❌ No | ❌ No |
| `cancelado_usuario` | ❌ Bloqueado | ❌ No | ❌ No |

---

## Campos Relacionados con Estados

### Nuevos Campos en `SolicitudMatriculacion`:

```python
# Fechas de tracking
fecha_aprobacion = DateTimeField(null=True)      # Cuando se aprueba
fecha_rechazo = DateTimeField(null=True)         # Cuando se rechaza
fecha_cancelacion = DateTimeField(null=True)     # Cuando se cancela

# Motivos
motivo_rechazo = TextField(null=True)            # Por qué se rechazó
motivo_cancelacion = TextField(null=True)        # Por qué se canceló

# Estado (ahora con max_length=30)
estado = CharField(max_length=30, choices=ESTADO_CHOICES)
```

---

## Métodos Helper del Modelo

### `is_valido()`
```python
def is_valido(self):
    """Verifica si el token aún es válido"""
    estados_terminales = ['aprobado', 'rechazado', 'cancelado_expiracion', 
                          'cancelado_usuario', 'token_usado']
    return timezone.now() < self.fecha_expiracion and self.estado not in estados_terminales
```

### `cancelar_por_expiracion()`
```python
def cancelar_por_expiracion(self):
    """Cancela la solicitud por expiración del token"""
    if self.estado in ['pendiente', 'correccion']:
        self.estado = 'cancelado_expiracion'
        self.fecha_cancelacion = timezone.now()
        self.motivo_cancelacion = f'Token expirado el {self.fecha_expiracion}'
        self.save()
        return True
    return False
```

### `cancelar_por_usuario(motivo='')`
```python
def cancelar_por_usuario(self, motivo=''):
    """Permite al usuario cancelar su solicitud"""
    if self.estado in ['pendiente', 'correccion']:
        self.estado = 'cancelado_usuario'
        self.fecha_cancelacion = timezone.now()
        self.motivo_cancelacion = motivo or 'Cancelado por el usuario'
        self.save()
        return True
    return False
```

### `marcar_token_usado()`
```python
def marcar_token_usado(self):
    """Marca el token como usado después de aprobar"""
    if self.estado == 'aprobado':
        self.estado = 'token_usado'
        self.save()
        return True
    return False
```

---

## Tareas Automáticas del Sistema

### 1. Cancelación Automática por Expiración
**Cuándo**: Diariamente a las 9:00 AM  
**Qué hace**:
- Busca solicitudes con `fecha_expiracion < ahora` y `estado IN ['pendiente', 'correccion']`
- Las marca como `cancelado_expiracion`
- Registra motivo automáticamente

**Código**: `core/scheduler.py` → `notificar_solicitudes_proximas_expirar()`

### 2. Marcado Automático de Token Usado
**Cuándo**: Inmediatamente después de aprobar solicitud  
**Qué hace**:
- Después de crear Usuario/Padre/Niño
- Cambia estado de `aprobado` → `token_usado`

**Código**: `core/views.py` → `aprobar_solicitud_matricula()`

### 3. Limpieza Automática de Archivos
**Cuándo**: Diariamente a las 3:00 AM  
**Qué hace**:
- Elimina archivos de solicitudes con estados terminales antiguos:
  - `cancelado_expiracion` (cualquier antigüedad)
  - `cancelado_usuario` (cualquier antigüedad)
  - `rechazado` (configurable, default 30 días)

**Código**: `core/management/commands/limpiar_archivos_solicitudes.py`

---

## Endpoints Nuevos

### Cancelar Solicitud (Usuario)
```
POST /matricula/publico/<token>/cancelar/
```

**Parámetros**:
- `motivo` (opcional): Razón de cancelación

**Respuesta exitosa**:
```json
{
  "success": true,
  "mensaje": "Su solicitud ha sido cancelada exitosamente."
}
```

**Errores**:
- `404`: Token no encontrado
- `400`: Estado no permite cancelación
- `500`: Error del servidor

---

## Notificaciones Relacionadas

### Al Cancelar por Usuario
- **Destinatario**: Madre comunitaria del hogar
- **Tipo**: `solicitud_cancelada`
- **Mensaje**: "El acudiente {email} canceló su solicitud de matrícula"
- **Nivel**: `info`

---

## Interfaz de Usuario

### Formulario Público - Mensajes por Estado

**Aprobado / Token Usado**:
```
✅ ¡Solicitud Aprobada!
Esta solicitud ya fue aprobada y el niño está matriculado.
El niño [Nombre] ya está matriculado en [Hogar].
```

**Rechazado**:
```
❌ Solicitud Rechazada
Esta solicitud fue rechazada por el hogar comunitario.
Motivo: [motivo_rechazo]
Si desea volver a aplicar, contacte al hogar comunitario.
```

**Cancelado por Expiración**:
```
⏰ Solicitud Cancelada por Expiración
Esta solicitud fue cancelada por expiración del plazo.
[motivo_cancelacion]
Si desea aplicar nuevamente, contacte al hogar comunitario.
```

**Cancelado por Usuario**:
```
🚫 Solicitud Cancelada
Esta solicitud fue cancelada.
Motivo: [motivo_cancelacion]
Esta solicitud fue cancelada. Si fue un error, contacte al hogar comunitario.
```

---

## Mejores Prácticas

### ✅ DO's
- Siempre validar estado antes de permitir ediciones
- Usar métodos helper (`cancelar_por_usuario()`, etc.) en lugar de asignar estado directamente
- Registrar timestamps en transiciones de estado
- Mostrar motivos de cancelación/rechazo al usuario
- Limpiar archivos de estados terminales

### ❌ DON'Ts
- No permitir modificar solicitudes en estados terminales
- No reutilizar tokens después de `aprobado`
- No eliminar solicitudes sin eliminar archivos asociados
- No permitir más de 3 intentos de corrección

---

## Testing

### Casos de Prueba Recomendados

1. **Flujo Normal**: `pendiente` → `aprobado` → `token_usado`
2. **Corrección**: `pendiente` → `correccion` → `aprobado`
3. **Rechazo**: `pendiente` → `rechazado`
4. **Expiración Automática**: `pendiente` → `cancelado_expiracion` (via scheduler)
5. **Cancelación Manual**: `pendiente` → `cancelado_usuario`
6. **Límite de Correcciones**: `correccion` (3 intentos) → `limite_excedido`

---

## Migración

**Archivo**: `core/migrations/0029_agregar_estados_cancelacion_y_campos_fecha.py`

**Cambios**:
- ✅ `estado` max_length: 20 → 30
- ✅ Agregados 3 nuevos estados a `ESTADO_CHOICES`
- ✅ Campo `fecha_rechazo`
- ✅ Campo `fecha_cancelacion`
- ✅ Campo `motivo_cancelacion`

---

**Última actualización**: Diciembre 2025  
**Versión del Sistema**: 2.0.0
