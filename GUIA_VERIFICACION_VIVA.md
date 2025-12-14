# 🧪 GUÍA DE VERIFICACIÓN EN VIVO

**Proyecto:** ICBF Conecta  
**Fecha:** 14 de Diciembre de 2025  
**Propósito:** Verificar todas las redirecciones y flujos funcionan en tiempo real

---

## 🚀 REQUISITOS PREVIOS

### Base de Datos
```bash
# Limpiar y recrear BD
python manage.py flush --no-input

# Cargar datos iniciales
python manage.py loaddata datos_iniciales.json

# Crear datos de prueba (usuario admin)
python manage.py createsuperuser
# Username: admin_test
# Email: admin@icbf.com
# Password: Admin123456
```

### Servidor
```bash
# Terminal 1: Iniciar servidor
python manage.py runserver

# Acceder a:
# http://localhost:8000
```

---

## 👨‍👧 VERIFICACIÓN PADRE

### Setup
```
1. Admin → Crear Padre
   - Documento: 12345678
   - Email: padre@test.com
   - Nombre: Juan Pérez
   - Password: Test123456

2. Admin → Crear Niño sin matricular (pendiente solicitud)
   - Padre: Juan Pérez
   - Nombre: Carlos
   - Documento: 87654321
```

### Test 1: Solicitar Matrícula ✅
```
Paso 1: Login padre@test.com / Test123456
  └─ Resultado esperado: Redirige a padre_dashboard
  └─ Verificar: Panel del padre visible

Paso 2: Click "Solicitar Matrícula"
  └─ URL esperada: /padre/solicitar-matricula/
  └─ Verificar: Formulario carga sin errores

Paso 3: Llenar formulario
  - Hogar: seleccionar uno disponible
  - Datos padre: pre-llenados
  - Datos hijo: completar
  
Paso 4: Click "Enviar Solicitud"
  └─ Resultado esperado: redirect('padre_dashboard')
  └─ Verificar: Mensaje de éxito
  └─ Verificar: Alerta aparece en dashboard
  └─ Verificar: Email enviado a madre
```

### Test 2: Ver Solicitud en Proceso ✅
```
Paso 1: En dashboard, click "Ver Solicitud"
  └─ URL esperada: /padre/solicitudes/{id}/
  └─ Verificar: Datos carga correctamente

Paso 2: Simular estado "correccion"
  └─ Admin → Panel Solicitudes → Devolver Corrección
  
Paso 3: Padre recarga dashboard
  └─ Verificar: Alerta roja "Corrección Necesaria" aparece
  
Paso 4: Click "Corregir Ahora"
  └─ URL esperada: /padre/solicitudes/{id}/corregir/
  └─ Verificar: Formulario con campos a corregir resaltados

Paso 5: Hacer cambios y click "Enviar Corrección"
  └─ Resultado esperado: redirect('padre_dashboard')
  └─ Verificar: Solicitud vuelve a estado "pendiente_revision"
```

### Test 3: Ver Desarrollo Hijo ✅
```
Paso 1: Admin → Crear evaluación desarrollo para niño de padre
  - Usar: Madre → Registrar Evaluación

Paso 2: Padre dashboard, click "Desarrollo" en card niño
  └─ URL esperada: /padre/desarrollo/{nino_id}/
  └─ Verificar: Timeline de evaluaciones visible
  └─ Verificar: Gráfico progreso carga

Paso 3: Click evaluación específica
  └─ Verificar: Detalles por dimensión visible
  └─ Verificar: Observaciones de madre visible
```

### Test 4: Solicitar Retiro ✅
```
Paso 1: Dashboard padre, click "Retiro" en card niño
  └─ Verificar: Modal se abre
  
Paso 2: Seleccionar motivo y click "Confirmar"
  └─ Resultado esperado: redirect('padre_dashboard')
  └─ Verificar: Niño ya no aparece en activos
  └─ Verificar: Email enviado a madre

Paso 3: Click "Mis Retiros" en navbar
  └─ URL esperada: /padre/mis-retiros/
  └─ Verificar: Solicitud aparece en lista

Paso 4: Click "Cancelar"
  └─ URL esperada: /padre/cancelar-retiro/{id}/
  └─ Resultado esperado: Solicitud cancelada
  └─ Verificar: Niño vuelve a estado anterior
```

---

## 👩‍🍼 VERIFICACIÓN MADRE

### Setup
```
1. Admin → Crear Madre
   - Documento: 98765432
   - Email: madre@test.com
   - Nombre: María García
   - Password: Test123456

2. Admin → Asignar hogar
   - Hogar: seleccionar uno
   - Madre: María García
```

### Test 1: Gestionar Niños ✅
```
Paso 1: Login madre@test.com / Test123456
  └─ Resultado esperado: Redirige a madre_dashboard
  
Paso 2: NavBar "Matrículas" → "Listar Niños"
  └─ URL esperada: /ninos/
  └─ Verificar: Niños del hogar listados

Paso 3: Click "Ver Ficha" en niño
  └─ URL esperada: /ninos/{id}/ver/
  └─ Verificar: Datos completos del niño

Paso 4: Click "Editar"
  └─ URL esperada: /ninos/{id}/editar/
  └─ Verificar: Formulario pre-llenado
  
Paso 5: Cambiar dato y guardar
  └─ Resultado esperado: redirect('listar_ninos')
  └─ Verificar: Cambio reflejado en lista
```

### Test 2: Registrar Planeación ✅
```
Paso 1: NavBar "Planeaciones"
  └─ URL esperada: /planeaciones/
  └─ Verificar: Lista planeaciones

Paso 2: Click "Nueva Planeación"
  └─ URL esperada: /planeaciones/registrar/
  └─ Verificar: Formulario carga

Paso 3: Llenar formulario
  - Dimensión: seleccionar
  - Objetivo: escribir
  - Estrategias: agregar
  
Paso 4: Click "Guardar"
  └─ Resultado esperado: redirect('planeaciones:lista_planeaciones')
  └─ Verificar: Planeación aparece en lista
  └─ Verificar: Documentaciones creadas
```

### Test 3: Registrar Evaluación ✅
```
Paso 1: NavBar "Desarrollo" → "Registrar Evaluación"
  └─ URL esperada: /desarrollo/generar/
  
Paso 2: Seleccionar niño y mes
  └─ Verificar: Dimensiones muestran

Paso 3: Checkear dimensiones a evaluar
  
Paso 4: Click "Guardar"
  └─ Resultado esperado: redirect('desarrollo:listar_desarrollos')
  └─ Verificar: Evaluación guardada
  └─ Verificar: Padre puede verla en dashboard
```

### Test 4: Registrar Novedades ✅
```
Paso 1: NavBar "Novedades"
  └─ URL esperada: /novedades/
  
Paso 2: Click "Nueva Novedad"
  └─ URL esperada: /novedades/create/
  
Paso 3: Llenar datos
  - Niño: seleccionar
  - Título: escribir
  - Descripción: escribir
  
Paso 4: Click "Guardar"
  └─ Resultado esperado: redirect('novedades:novedades_list')
  └─ Verificar: Novedad guardada
  └─ Verificar: Padre notificado
```

### Test 5: Procesar Retiro ✅
```
Paso 1: NavBar "Retiros"
  └─ URL esperada: /madre/solicitudes-retiro/
  └─ Verificar: Solicitudes pendientes listadas

Paso 2: Click "Procesar" en solicitud
  └─ Verificar: Modal confirmación

Paso 3: Click "Confirmar Procesamiento"
  └─ Resultado esperado: redirect('madre_ver_retiros')
  └─ Verificar: Solicitud moved a "procesadas"
  └─ Verificar: Padre notificado
```

---

## 👨‍💼 VERIFICACIÓN ADMINISTRADOR

### Setup
```
Admin ya creado (createsuperuser)
```

### Test 1: Panel Revisión Solicitudes ✅
```
Paso 1: Login admin_test / Admin123456
  └─ Resultado esperado: Redirige a dashboard_admin
  
Paso 2: NavBar "Solicitudes" → "Panel Revisión"
  └─ URL esperada: /solicitudes/panel-revision/
  └─ Verificar: Solicitudes por estado (Pendiente, Corrección, etc)

Paso 3: Click solicitud en "Pendiente"
  └─ URL esperada: /solicitudes/{id}/detalle/
  └─ Verificar: Datos completos visibles

Paso 4: Click "Aprobar"
  └─ Resultado esperado: redirect('panel_revision_solicitudes')
  └─ Verificar: Solicitud move a "Aprobada"
  └─ Verificar: Niño creado en sistema
  └─ Verificar: Padre recibe email
  └─ Verificar: Madre notificada

Paso 5: Click solicitud y "Rechazar"
  └─ Modal pide motivo
  └─ Resultado esperado: redirect('panel_revision_solicitudes')
  └─ Verificar: Padre recibe email con motivo

Paso 6: Click solicitud y "Devolver a Corrección"
  └─ Modal pide campos a corregir
  └─ Resultado esperado: redirect('panel_revision_solicitudes')
  └─ Verificar: Padre recibe email
  └─ Verificar: Puede "Corregir Solicitud" desde dashboard
```

### Test 2: Gestión Hogares ✅
```
Paso 1: NavBar "Hogares"
  └─ URL esperada: /hogares/
  
Paso 2: Click hogar
  └─ URL esperada: /hogares/{id}/detalle/
  └─ Verificar: Madre asignada
  └─ Verificar: Niños listados
  
Paso 3: Click "Editar"
  └─ Verificar: Formulario carga
  
Paso 4: Click "Ver Visita Técnica"
  └─ URL esperada: /visitas/
  └─ Verificar: Historial visitas
```

### Test 3: Visitas Técnicas ✅
```
Paso 1: NavBar "Hogares" → "Visitas Técnicas"
  └─ URL esperada: /visitas/
  
Paso 2: Click "Agendar Visita" en hogar pendiente
  └─ URL esperada: /visitas/agendar/{hogar_id}/
  
Paso 3: Seleccionar fecha y agente
  
Paso 4: Click "Agendar"
  └─ Resultado esperado: redirect('listar_visitas_tecnicas')
  └─ Verificar: Visita aparece agendada
  
Paso 5: Click "Realizar Visita"
  └─ URL esperada: /hogares/{id}/realizar-visita/
  
Paso 6: Llenar acta
  - Observaciones
  - Recomendaciones
  - Estado hogar
  
Paso 7: Click "Guardar"
  └─ Verificar: Acta guardada
  └─ Verificar: Madre notificada
```

---

## 🔐 VERIFICACIÓN SEGURIDAD

### Test 1: IDOR Protection (Acceso No Autorizado) ✅
```
Paso 1: Login como Padre 1
  └─ ID Niño de Padre 1: 10

Paso 2: Intentar acceder URL directa otro padre
  └─ URL: /padre/nino/99/perfil/  (niño de Padre 2)
  └─ Resultado esperado: Error 404 o redirect

Paso 3: Verificar mismo padres no pueden ver niños otros
  └─ URL: /padre/desarrollo/99/  (niño otro padre)
  └─ Resultado esperado: Error 404
```

### Test 2: Acceso No Autenticado ✅
```
Paso 1: Logout (borrar session)

Paso 2: Intentar acceder /padre/solicitar-matricula/
  └─ Resultado esperado: Redirect a /login/

Paso 3: Intentar acceder /madre/ninos/
  └─ Resultado esperado: Redirect a /login/

Paso 4: Intentar acceder /solicitudes/panel-revision/
  └─ Resultado esperado: Redirect a /login/
```

### Test 3: CSRF Protection ✅
```
Paso 1: Abrir network tab del navegador

Paso 2: Enviar formulario (ej: solicitar matrícula)
  └─ Verificar en HTTP POST: csrftoken enviado

Paso 3: Remover manualmente token y intentar enviar
  └─ Resultado esperado: Error 403 CSRF
```

### Test 4: Roles Separados ✅
```
Paso 1: Login como Padre

Paso 2: Intentar acceder /madre/ninos/
  └─ Resultado esperado: Access Denied (403) o redirect

Paso 3: Intentar acceder /solicitudes/panel-revision/
  └─ Resultado esperado: Access Denied

Paso 4: Login como Madre

Paso 5: Intentar acceder /padre/solicitar-matricula/
  └─ Resultado esperado: Access Denied

Paso 6: Intentar acceder /solicitudes/panel-revision/
  └─ Resultado esperado: Access Denied
```

---

## 📧 VERIFICACIÓN EMAILS

### Setup
```
Ver en consola los emails (modo DEBUG = True)
O revisar EmailLog en admin
```

### Test Emails Enviados
```
✅ Solicitud matrícula enviada
   └─ Admin notification email

✅ Corrección solicitada
   └─ Padre notification email

✅ Solicitud aprobada
   └─ Padre notification email

✅ Solicitud rechazada
   └─ Padre notification email con motivo

✅ Solicitud retiro procesada
   └─ Padre notification email

✅ Novedad registrada
   └─ Padre notification email
```

---

## 📊 VERIFICACIÓN DATOS

### Base de Datos Integrity
```bash
# Terminal: Ver modelo integración
python manage.py shell

>>> from core.models import Usuario, Padre, MadreComunitaria, Nino
>>> Padre.objects.count()  # Debe > 0

>>> from core.models import SolicitudMatriculacion
>>> SolicitudMatriculacion.objects.count()  # Debe > 0 después tests

>>> from core.models import SolicitudRetiroMatricula  
>>> SolicitudRetiroMatricula.objects.count()  # Debe > 0 después test retiro
```

### Verificar Relaciones
```bash
>>> padre = Padre.objects.first()
>>> padre.usuario.nombres  # Debe tener nombre
>>> padre.ninos.count()    # Debe tener niños
>>> nino = padre.ninos.first()
>>> nino.hogar.nombre      # Debe tener hogar
>>> nino.hogar.madre.usuario.nombres  # Debe tener madre
```

---

## 📋 CHECKLIST FINAL

```
INTERFAZ USUARIO
 [ ] Dashboard padre carga sin errores
 [ ] Dashboard madre carga sin errores
 [ ] Dashboard admin carga sin errores
 [ ] Todos los botones son clicables
 [ ] Todos los links navegan correctamente
 [ ] Alertas se muestran en color correcto
 [ ] Formularios validan datos
 [ ] Mensajes de éxito aparecen

FUNCIONALIDAD
 [ ] Solicitudes matrícula se pueden crear
 [ ] Solicitudes matrícula se pueden corregir
 [ ] Solicitudes retiro se pueden crear
 [ ] Evaluaciones se pueden registrar
 [ ] Planeaciones se pueden crear
 [ ] Novedades se pueden registrar
 [ ] Emails se envían

SEGURIDAD
 [ ] No se puede acceder sin login
 [ ] No se puede acceder otro usuario datos
 [ ] CSRF tokens validados
 [ ] Roles protegidos correctamente
 [ ] Archivos no pueden > 5MB

BASE DE DATOS
 [ ] Datos se guardan correctamente
 [ ] Relaciones intactas
 [ ] No hay duplicados
 [ ] Estados coherentes
```

---

## 🚨 Si Algo Falla

### Error 404 en URL
```
1. Verificar URL en urls.py existe
2. Verificar nombre en urls.py
3. Verificar name= parámetro
4. Ejecutar: python manage.py check
```

### Error 403 Forbidden
```
1. Verificar usuario está loguead
2. Verificar rol es correcto
3. Verificar decorador @rol_requerido
4. Revisar logs de acceso
```

### Error 500 Internal Server Error
```
1. Ver consola de Django (stdout)
2. Revisar logs de aplicación
3. Verificar base de datos está conectada
4. Ejecutar: python manage.py migrate
```

### Email no enviado
```
1. Revisar configuración SMTP en .env
2. Revisar EmailLog en admin
3. Revisar console (modo DEBUG)
4. Verificar dirección email válida
```

### Datos no guardan
```
1. Revisar validación formulario
2. Verificar campos requeridos llenados
3. Revisar logs de base de datos
4. Ejecutar: python manage.py migrate
```

---

**Guía Verificación Completada:** 14 de Diciembre de 2025 ✅
