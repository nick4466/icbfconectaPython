# 📋 Funcionalidad: Solicitud de Retiro de Matrícula - IMPLEMENTACIÓN COMPLETA

## ✅ RESUMEN EJECUTIVO

Se ha implementado exitosamente la **funcionalidad de Solicitud de Retiro de Matrícula** en ICBF Conecta. Esta funcionalidad permite:

1. **Padres**: Solicitar el retiro de sus hijos del hogar comunitario
2. **Madres Comunitarias**: Revisar, aprobar o rechazar las solicitudes
3. **Notificaciones**: Automatizadas por email y notificaciones in-app

---

## 🏗️ ARQUITECTURA IMPLEMENTADA

### 1. BASE DE DATOS (Models)

**Archivo**: `core/models.py`
**Modelo**: `SolicitudRetiroMatricula`

```python
class SolicitudRetiroMatricula(models.Model):
    - nino: ForeignKey → Niño
    - padre: ForeignKey → Padre
    - hogar: ForeignKey → HogarComunitario
    - motivo: CharField (cambio_domicilio, cambio_cuidador, etc.)
    - descripcion: TextField (opcional)
    - estado: CharField (pendiente, aprobado, rechazado, cancelado_padre)
    - fecha_solicitud: DateTimeField (auto_now_add)
    - fecha_respuesta: DateTimeField (null=True)
    - observaciones_madre: TextField (null=True)
    - respondida_por: ForeignKey → Usuario (null=True)
    
    Métodos:
    - aprobar(usuario, observaciones): Aprueba y cambia estado del niño a "retirado"
    - rechazar(usuario, observaciones): Rechaza pero mantiene estado del niño
    - cancelar_por_padre(): Permite que el padre cancele su solicitud pendiente
```

**Migración**: `core/migrations/0045_crear_solicitud_retiro_matricula.py`
- ✅ Aplicada exitosamente a la base de datos
- Índices: (nino, estado), (padre, fecha), (hogar, estado)

---

### 2. VISTAS (Views)

**Archivo**: `core/views.py` (Líneas 7320-7516)

#### VISTAS DEL PADRE:

**`padre_solicitar_retiro(request, nino_id)` [AJAX POST]**
- URL: `POST /padre/solicitar-retiro/{nino_id}/`
- Validaciones:
  - Usuario es padre
  - El niño le pertenece
  - Niño está en estado "activo"
  - No hay solicitud pendiente previa
- Acciones:
  - Crea solicitud de retiro
  - Envía email a la madre
  - Crea notificación in-app

**`padre_ver_retiros(request)` [GET]**
- URL: `GET /padre/mis-retiros/`
- Muestra solicitudes pendientes e historial
- Dos pestañas: Pendientes y Procesadas

**`padre_cancelar_retiro(request, solicitud_id)` [AJAX POST]**
- URL: `POST /padre/cancelar-retiro/{solicitud_id}/`
- Solo si está pendiente
- Cambia estado a "cancelado_padre"

#### VISTAS DE LA MADRE:

**`madre_ver_retiros_solicitudes(request)` [GET]**
- URL: `GET /madre/solicitudes-retiro/`
- Muestra solicitudes pendientes de su hogar
- Muestra historial de últimos 30 días

**`madre_procesar_retiro(request, solicitud_id)` [AJAX POST]**
- URL: `POST /madre/procesar-retiro/{solicitud_id}/`
- Parámetros: accion (aprobar/rechazar), observaciones
- Acciones:
  - Si APRUEBA: Cambia estado del niño a "retirado"
  - Si RECHAZA: Mantiene estado "activo"
  - Envía email de respuesta
  - Crea notificación para el padre

#### FUNCIONES DE EMAIL:

**`enviar_email_retiro_padre(solicitud)`**
- Template: `emails/solicitud_retiro_padre.html`
- Notifica a la madre sobre nueva solicitud

**`enviar_email_respuesta_retiro(solicitud, accion)`**
- Template: `emails/retiro_aprobado.html` o `retiro_rechazado.html`
- Notifica al padre sobre respuesta

---

### 3. TEMPLATES (Interfaz)

#### Componentes Reutilizables:

**`padre/modal_solicitar_retiro.html`**
- Modal para solicitar retiro
- Campos: Motivo (dropdown) + Descripción (textarea)
- Validaciones en JS
- Contador de caracteres

**`padre/mis_retiros.html` (Página Completa)**
- Tablas de solicitudes pendientes e historial
- Botones de acciones (cancelar, ver detalles)
- Estados visuales por color

**`madre/solicitudes_retiro.html` (Página Completa)**
- Gestión de solicitudes del hogar
- Modal para aprobar/rechazar
- Campo de observaciones obligatorio para rechazo

#### Templates de Email:

- `emails/solicitud_retiro_padre.html` - Nueva solicitud
- `emails/retiro_aprobado.html` - Aprobación
- `emails/retiro_rechazado.html` - Rechazo

#### Integraciones Existentes:

- **`padre/dashboard.html`**: Botón "Solicitar Retiro" en tarjetas de niños
- **`padre/navbar_padre.html`**: Link "Mis Retiros" en nav
- **`madre/navbar_madre.html`**: Link "Retiros" en nav

---

### 4. RUTAS URL

**Archivo**: `icbfconecta/urls.py` (Líneas 199-205)

```python
# PADRE - Solicitar y gestionar retiros
path('padre/solicitar-retiro/<int:nino_id>/', views.padre_solicitar_retiro, name='padre_solicitar_retiro'),
path('padre/mis-retiros/', views.padre_ver_retiros, name='padre_ver_retiros'),
path('padre/cancelar-retiro/<int:solicitud_id>/', views.padre_cancelar_retiro, name='padre_cancelar_retiro'),

# MADRE - Gestionar retiros del hogar
path('madre/solicitudes-retiro/', views.madre_ver_retiros_solicitudes, name='madre_ver_retiros'),
path('madre/procesar-retiro/<int:solicitud_id>/', views.madre_procesar_retiro, name='madre_procesar_retiro'),
```

---

## 📊 FLUJO DE LA FUNCIONALIDAD

### 1️⃣ PADRE SOLICITA RETIRO

```
Padre ve dashboard
    ↓
[Botón "Solicitar Retiro" en tarjeta del niño]
    ↓
Se abre modal (padre/modal_solicitar_retiro.html)
    ↓
Padre completa:
  - Motivo (dropdown)
  - Descripción (optional)
    ↓
POST → /padre/solicitar-retiro/{nino_id}/
    ↓
Validaciones:
  ✓ Es padre del niño
  ✓ Niño en estado "activo"
  ✓ No hay solicitud pendiente
    ↓
CREA: SolicitudRetiroMatricula (estado='pendiente')
ENVIA: Email a madre (solicitud_retiro_padre.html)
CREA: Notificación in-app para madre
RESPUESTA: JSON success
    ↓
Padre ve toast "✅ Solicitud enviada"
```

### 2️⃣ MADRE REVISA Y PROCESA

```
Madre ve navbar → [Retiros]
    ↓
GET → /madre/solicitudes-retiro/
    ↓
Ve lista de solicitudes pendientes
    ↓
[Botón "Aprobar" o "Rechazar" en cada solicitud]
    ↓
Se abre modal (madre/modal_procesar_retiro.html)
    ↓
Madre selecciona acción:
  - APROBAR: (observaciones opcional)
  - RECHAZAR: (observaciones obligatorio)
    ↓
POST → /madre/procesar-retiro/{solicitud_id}/
  accion=aprobar/rechazar
  observaciones=texto
    ↓
Validaciones:
  ✓ Es madre del hogar
  ✓ Solicitud en estado "pendiente"
  ✓ Si rechaza: observaciones no vacías
    ↓
SI APRUEBA:
  - solicitud.aprobar(usuario, observaciones)
  - nino.estado → 'retirado'
  - ENVIA: Email aprobado
  - CREA: Notificación "✅ APROBADA"
    
SI RECHAZA:
  - solicitud.rechazar(usuario, observaciones)
  - nino.estado → sigue siendo 'activo'
  - ENVIA: Email rechazado
  - CREA: Notificación "❌ RECHAZADA"
    ↓
Página recarga automáticamente
```

### 3️⃣ PADRE VE HISTORIAL

```
Padre → Navbar [Mis Retiros]
    ↓
GET → /padre/mis-retiros/
    ↓
Pestaña 1: PENDIENTES
  - Solicitudes en proceso
  - Botón [Cancelar solicitud]
    
Pestaña 2: HISTORIAL
  - Solicitudes aprobadas/rechazadas
  - Muestra observaciones de la madre
    ↓
POST → /padre/cancelar-retiro/{solicitud_id}/ (si requiere)
  - Cambia estado a 'cancelado_padre'
```

---

## 🔐 SEGURIDAD

### Control de Acceso:
- ✅ `@login_required` en todas las vistas
- ✅ Validación que padre solo vea sus niños
- ✅ Validación que madre solo vea su hogar
- ✅ Solo madre puede procesar solicitudes de su hogar

### Validaciones de Negocio:
- ✅ Solo niños "activos" pueden ser retirados
- ✅ Una sola solicitud pendiente por niño
- ✅ Transacciones atómicas con `transaction.atomic()`
- ✅ Observaciones obligatorias al rechazar

---

## 📧 SISTEMA DE NOTIFICACIONES

### Por Email:

1. **Cuando padre solicita**: `solicitud_retiro_padre.html`
   - Destinatario: Madre comunitaria
   - Información: Niño, motivo, descripción

2. **Cuando madre aprueba**: `retiro_aprobado.html`
   - Destinatario: Padre
   - Estado: RETIRADO ✅

3. **Cuando madre rechaza**: `retiro_rechazado.html`
   - Destinatario: Padre
   - Motivo y observaciones

### In-App (Sistema de Notificaciones):

- ✅ Notificación para madre cuando padre solicita
- ✅ Notificación para padre cuando madre responde
- ✅ Íconos y colores según tipo (info/warning/success)

---

## 🧪 PRUEBAS REALIZADAS

### ✅ Validaciones:

- [x] Django `manage.py check` - Sin errores
- [x] Migración aplicada exitosamente
- [x] Models con relaciones correctas
- [x] URLs configuradas y accesibles
- [x] Templates sin errores de sintaxis

### ✅ Flujo Manual:

- [x] Padre puede ver botón "Solicitar Retiro"
- [x] Modal se abre correctamente
- [x] Validación de campos funciona
- [x] AJAX POST envía datos correctamente
- [x] Base de datos crea registro
- [x] Emails se generan (templates)
- [x] Madre ve solicitud en panel
- [x] Madre puede aprobar/rechazar
- [x] Estados se actualizan correctamente

---

## 📱 INTERFACES USUARIO

### Padre - Dashboard
```
┌─────────────────────────────────────┐
│ ICBF Conecta                        │
├─────────────────────────────────────┤
│                                     │
│  Tarjeta Niño: "Juan Pérez"        │
│  ┌─────────────────────────────┐   │
│  │ [Foto] Juan Pérez           │   │
│  │ Hogar: Casa Hogar "Alegría" │   │
│  │                             │   │
│  │ [Desarrollo]  [Novedades]   │   │
│  │ [Asistencia]  [Retiro] ⬅    │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Padre - Modal Retiro
```
┌─────────────────────────────────────┐
│ ⚠️ Solicitar Retiro de Matrícula   │
├─────────────────────────────────────┤
│ Motivo: [Cambio de domicilio ▼]    │
│ Descripción: [___________]          │
│              [___________]          │
│                                     │
│ [Cancelar]      [Enviar Solicitud] │
└─────────────────────────────────────┘
```

### Madre - Solicitudes Retiro
```
┌────────────────────────────────────────┐
│ Solicitudes de Retiro                  │
│ [Pendientes 3]  [Procesadas 5]        │
├────────────────────────────────────────┤
│ ┌──────────────────────────────────┐   │
│ │ Juan Pérez          [PENDIENTE]   │   │
│ │ Por: Carlos López                 │   │
│ │ Motivo: Cambio de domicilio       │   │
│ │                                   │   │
│ │ [Aprobar]  [Rechazar]             │   │
│ └──────────────────────────────────┘   │
└────────────────────────────────────────┘
```

---

## 📦 ARCHIVOS MODIFICADOS/CREADOS

### ✅ Creados:
1. `core/migrations/0045_crear_solicitud_retiro_matricula.py`
2. `templates/padre/modal_solicitar_retiro.html`
3. `templates/padre/mis_retiros.html`
4. `templates/madre/solicitudes_retiro.html`
5. `templates/emails/solicitud_retiro_padre.html`
6. `templates/emails/retiro_aprobado.html`
7. `templates/emails/retiro_rechazado.html`

### ✅ Modificados:
1. `core/models.py` - Agregado modelo SolicitudRetiroMatricula
2. `core/views.py` - Agregadas 5 vistas nuevas + 2 funciones email
3. `icbfconecta/urls.py` - Agregadas 5 rutas URL nuevas
4. `templates/padre/dashboard.html` - Integrado botón de retiro
5. `templates/padre/navbar_padre.html` - Agregado link "Mis Retiros"
6. `templates/madre/navbar_madre.html` - Agregado link "Retiros"

---

## 🚀 CÓMO USAR

### Para el Padre:

1. Ve al Dashboard
2. Encuentra la tarjeta del niño que deseas retirar
3. Haz clic en el botón **"Solicitar Retiro"**
4. Completa el modal:
   - Selecciona el **Motivo**
   - (Opcional) Agrega una **Descripción**
5. Haz clic en **"Enviar Solicitud"**
6. Verás un toast de confirmación
7. Puedes ver el estado en **"Mis Retiros"**

### Para la Madre:

1. En la Navbar, haz clic en **"Retiros"**
2. Verás las solicitudes pendientes de tu hogar
3. Para cada solicitud:
   - Haz clic en **"Aprobar"** o **"Rechazar"**
   - Si rechazas, debes escribir el motivo
4. Confirma la acción
5. El padre recibirá un email automático
6. Puedes ver el historial en la pestaña **"Procesadas"**

---

## 🔧 CONFIGURACIÓN REQUERIDA

Asegúrate que en `settings.py` tengas configurados:

```python
# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'tu-servidor-smtp'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-contraseña'
DEFAULT_FROM_EMAIL = 'tu-email@gmail.com'
```

---

## 📋 CHECKLIST FINAL

- [x] Modelo creado y migración aplicada
- [x] Vistas implementadas (padre y madre)
- [x] URLs configuradas
- [x] Templates creados
- [x] Emails diseñados
- [x] Integraciones en dashboards
- [x] Notificaciones in-app
- [x] Validaciones de seguridad
- [x] `manage.py check` sin errores
- [x] Documentación completa

---

## 📞 SOPORTE

Si encuentras problemas:

1. Verifica que `manage.py check` no reporte errores
2. Revisa los logs del servidor para excepciones
3. Asegúrate que la migración 0045 está aplicada: `manage.py migrate`
4. Verifica la configuración de email en `settings.py`
5. Revisa permisos de carpeta `templates/`

---

**Implementación completada: ✅ FUNCIONAL**
**Fecha**: 2024
**Estado**: Listo para producción
