# ✅ CHECKLIST DE VERIFICACIÓN - FUNCIONALIDAD RETIRO

## 🔍 VERIFICACIÓN TÉCNICA

### Base de Datos

- [ ] Migración 0045 aplicada
  ```bash
  python manage.py migrate --list | grep 0045_crear_solicitud_retiro_matricula
  ```
  Debe mostrar: `[X] 0045_crear_solicitud_retiro_matricula`

- [ ] Tabla `core_solicitudretiromatricula` existe
  ```bash
  python manage.py dbshell
  .tables
  ```
  Debe incluir: `core_solicitudretiromatricula`

- [ ] Modelo importable
  ```bash
  python manage.py shell
  >>> from core.models import SolicitudRetiroMatricula
  >>> SolicitudRetiroMatricula
  <class 'core.models.SolicitudRetiroMatricula'>
  ```

### Vistas

- [ ] Todas las funciones importan correctamente
  ```bash
  python -m py_compile core/views.py
  ```
  (Sin output = sin errores)

- [ ] Las 5 vistas están definidas:
  - [ ] `padre_solicitar_retiro()`
  - [ ] `padre_ver_retiros()`
  - [ ] `padre_cancelar_retiro()`
  - [ ] `madre_ver_retiros_solicitudes()`
  - [ ] `madre_procesar_retiro()`

- [ ] Las 2 funciones de email están definidas:
  - [ ] `enviar_email_retiro_padre()`
  - [ ] `enviar_email_respuesta_retiro()`

### URLs

- [ ] Las 5 rutas están registradas
  ```bash
  python manage.py show_urls | grep retiro
  ```
  Debe mostrar:
  ```
  padre/solicitar-retiro/<int:nino_id>/   padre_solicitar_retiro
  padre/mis-retiros/                       padre_ver_retiros
  padre/cancelar-retiro/<int:solicitud_id>/ padre_cancelar_retiro
  madre/solicitudes-retiro/                madre_ver_retiros
  madre/procesar-retiro/<int:solicitud_id>/ madre_procesar_retiro
  ```

### Templates

- [ ] `templates/padre/modal_solicitar_retiro.html` existe
- [ ] `templates/padre/mis_retiros.html` existe
- [ ] `templates/madre/solicitudes_retiro.html` existe
- [ ] `templates/emails/solicitud_retiro_padre.html` existe
- [ ] `templates/emails/retiro_aprobado.html` existe
- [ ] `templates/emails/retiro_rechazado.html` existe

### Integraciones

- [ ] `templates/padre/dashboard.html` incluye modal
  ```bash
  grep -n "modal_solicitar_retiro" templates/padre/dashboard.html
  ```
  Debe mostrar una línea con `include`

- [ ] `templates/padre/dashboard.html` tiene botón de retiro
  ```bash
  grep -n "Solicitar Retiro" templates/padre/dashboard.html
  ```
  Debe mostrar una línea

- [ ] `templates/padre/navbar_padre.html` tiene link
  ```bash
  grep -n "padre_ver_retiros" templates/padre/navbar_padre.html
  ```

- [ ] `templates/madre/navbar_madre.html` tiene link
  ```bash
  grep -n "madre_ver_retiros" templates/madre/navbar_madre.html
  ```

---

## 🧪 VERIFICACIÓN FUNCIONAL

### Paso 1: Padre accede al dashboard

- [ ] Navega a `/dashboard/padre/`
- [ ] Ve sus niños en tarjetas
- [ ] Niños en estado "activo" muestran botón "Solicitar Retiro"
- [ ] Niños en otro estado NO muestran el botón

### Paso 2: Padre abre modal

- [ ] Haz clic en "Solicitar Retiro"
- [ ] Se abre modal con título "Solicitar Retiro de Matrícula"
- [ ] Modal tiene:
  - [ ] Dropdown de motivos
  - [ ] Textarea de descripción
  - [ ] Botón "Cancelar"
  - [ ] Botón "Enviar Solicitud"

### Paso 3: Padre completa y envía

- [ ] Selecciona un motivo
- [ ] Escribe descripción (opcional)
- [ ] Haz clic "Enviar Solicitud"
- [ ] Ver respuesta:
  - [ ] POST a `/padre/solicitar-retiro/{nino_id}/` en inspector
  - [ ] Response status: 200
  - [ ] Response JSON: `{"status": "ok", "mensaje": "..."}`
  - [ ] Toast verde aparece: "✅ Solicitud enviada"

### Paso 4: Verifica base de datos

- [ ] La solicitud se creó
  ```bash
  python manage.py shell
  >>> from core.models import SolicitudRetiroMatricula
  >>> SolicitudRetiroMatricula.objects.last()
  <SolicitudRetiroMatricula: ...>
  ```

- [ ] Los campos están completos:
  ```bash
  >>> s = SolicitudRetiroMatricula.objects.last()
  >>> s.estado
  'pendiente'
  >>> s.motivo
  'cambio_domicilio'
  ```

### Paso 5: Padre ve historial

- [ ] Navega a `/padre/mis-retiros/`
- [ ] Pestaña "Pendientes" muestra la solicitud
- [ ] Muestra:
  - [ ] Nombre del niño
  - [ ] Hogar
  - [ ] Motivo
  - [ ] Descripción
  - [ ] Fecha de solicitud
  - [ ] Botón "Cancelar solicitud"

### Paso 6: Madre accede a panel

- [ ] Navega a `/madre/solicitudes-retiro/`
- [ ] Pestaña "Pendientes" muestra la solicitud
- [ ] Card muestra:
  - [ ] Nombre del niño
  - [ ] ID del niño
  - [ ] Nombre del padre
  - [ ] Email del padre
  - [ ] Motivo
  - [ ] Descripción
  - [ ] Botones "Aprobar" y "Rechazar"

### Paso 7: Madre aprueba

- [ ] Haz clic "Aprobar"
- [ ] Se abre modal para procesar
- [ ] Escribir observaciones (opcional)
- [ ] Haz clic "Confirmar Aprobación"
- [ ] POST a `/madre/procesar-retiro/{id}/` con:
  - [ ] `accion=aprobar`
  - [ ] `observaciones=...`
- [ ] Response: `{"status": "ok"}`
- [ ] Toast verde: "Retiro APROBADO"
- [ ] Página recarga

### Paso 8: Verifica cambios en DB

- [ ] Estado de la solicitud cambió:
  ```bash
  >>> s.refresh_from_db()
  >>> s.estado
  'aprobado'
  >>> s.fecha_respuesta
  datetime.datetime(...)
  ```

- [ ] Estado del niño cambió:
  ```bash
  >>> s.nino.estado
  'retirado'
  ```

### Paso 9: Prueba rechazo

- [ ] Crea otra solicitud (paso 1-3)
- [ ] Madre haz clic "Rechazar"
- [ ] Modal pide observaciones (obligatorio)
- [ ] Escribir motivo: "El niño está adaptándose bien"
- [ ] Haz clic "Confirmar Rechazo"
- [ ] Verifica:
  ```bash
  >>> s = SolicitudRetiroMatricula.objects.last()
  >>> s.estado
  'rechazado'
  >>> s.nino.estado
  'activo'  # Sin cambios
  ```

### Paso 10: Padre cancela solicitud

- [ ] Crea otra solicitud (paso 1-3)
- [ ] Padre ve "Mis Retiros" → Pendientes
- [ ] Haz clic "Cancelar solicitud"
- [ ] Confirmar en popup
- [ ] Verifica:
  ```bash
  >>> s.refresh_from_db()
  >>> s.estado
  'cancelado_padre'
  ```

---

## 📧 VERIFICACIÓN DE EMAILS

### Email de nueva solicitud

- [ ] Madre recibe email cuando padre solicita
- [ ] Email contiene:
  - [ ] Nombre del padre
  - [ ] Nombre del niño
  - [ ] Motivo seleccionado
  - [ ] Descripción
  - [ ] Link "Ver Solicitud en el Panel"
  - [ ] Instrucciones claras

### Email de aprobación

- [ ] Padre recibe email cuando madre aprueba
- [ ] Asunto contiene: "APROBADA"
- [ ] Email muestra:
  - [ ] Estado: "RETIRADO ✅"
  - [ ] Fecha de aprobación
  - [ ] Observaciones de la madre
  - [ ] Próximos pasos

### Email de rechazo

- [ ] Padre recibe email cuando madre rechaza
- [ ] Asunto contiene: "RECHAZADA"
- [ ] Email muestra:
  - [ ] Estado: "ACTIVO"
  - [ ] Motivo del rechazo
  - [ ] Opción de contactar

---

## 🔐 VERIFICACIÓN DE SEGURIDAD

### Validaciones de acceso

- [ ] Usuario no autenticado no puede acceder a `/padre/solicitar-retiro/`
  - Redirecciona a login ✓

- [ ] Padre solo ve sus propios niños
  - [ ] Intenta acceder a niño de otro padre
  - [ ] Recibe error 404 ✓

- [ ] Madre solo ve su hogar
  - [ ] Intenta procesar solicitud de otro hogar
  - [ ] Recibe error 403 ✓

### Validaciones de negocio

- [ ] No se puede solicitar retiro de niño inactivo
  - [ ] Botón no aparece en dashboard ✓
  - [ ] Si accedes manualmente a URL: Error ✓

- [ ] No se puede tener 2 solicitudes pendientes
  - [ ] Crea primera solicitud
  - [ ] Intenta crear segunda
  - [ ] Recibe error: "Ya existe solicitud pendiente" ✓

- [ ] Madre debe escribir motivo al rechazar
  - [ ] Intenta rechazar sin observaciones
  - [ ] Formulario requiere campo ✓

---

## 📊 VERIFICACIÓN VISUAL

### Dashboard Padre

- [ ] Tarjeta de niño activo muestra botón rojo "Solicitar Retiro"
- [ ] Botón está bien posicionado (no superpone otros elementos)
- [ ] Al hacer hover, botón cambia color
- [ ] Modal aparece centrado en la pantalla

### Modal de Solicitud

- [ ] Modal tiene encabezado rojo con icono ⚠️
- [ ] Campo de motivo es dropdown (no texto)
- [ ] Textarea para descripción tiene placeholder
- [ ] Contador de caracteres actualiza en tiempo real
- [ ] Botones están alineados en el pie del modal

### Panel de Solicitudes (Madre)

- [ ] Dos pestañas (Pendientes / Procesadas) están visibles
- [ ] Tarjetas de solicitudes tienen fondo blanco
- [ ] Encabezado rojo para solicitudes pendientes
- [ ] Botones de acción están bien visibles
- [ ] Colores por estado (rojo=pendiente, verde=aprobado, naranja=rechazado)

---

## ⚠️ PROBLEMAS CONOCIDOS A REVISAR

- [ ] ¿El modal se cierra después de enviar?
- [ ] ¿La página recarga automáticamente?
- [ ] ¿Los emails se envían (si SMTP está configurado)?
- [ ] ¿Las notificaciones in-app aparecen?
- [ ] ¿Los Toast messages tienen buen contraste?

---

## 🎯 RESULTADO FINAL

Si todos los checks están ✓, entonces:

✅ **LA FUNCIONALIDAD ESTÁ 100% OPERATIVA**

---

## 📝 NOTAS PARA EL DESARROLLADOR

1. **Email en desarrollo**: Si no quieres recibir 1000 emails, configura:
   ```python
   # settings.py
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```
   Los emails aparecerán en la consola en lugar de enviarse.

2. **Base de datos de prueba**: Para testing rápido:
   ```bash
   python manage.py shell
   from core.models import *
   padre = Padre.objects.first()
   nino = padre.hijo_padre.first()
   SolicitudRetiroMatricula.objects.create(
       padre=padre, nino=nino, hogar=nino.hogar,
       motivo='cambio_domicilio'
   )
   ```

3. **Limpiar solicitudes de test**:
   ```bash
   python manage.py shell
   from core.models import SolicitudRetiroMatricula
   SolicitudRetiroMatricula.objects.all().delete()
   ```

---

**Este checklist asegura que la funcionalidad funcione correctamente en 100% de los casos.**
