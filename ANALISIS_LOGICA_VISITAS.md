# 🔍 ANÁLISIS COMPLETO: LÓGICA DE VISITAS Y CREACIÓN DE HOGARES

## 📊 ESTADO ACTUAL DEL SISTEMA

### ✅ Funcionalidades Implementadas Correctamente

1. **Creación de Madre y Hogar** (`crear_madre`)
   - ✅ Formulario multi-paso (Usuario → Madre → Hogar)
   - ✅ Asignación de localidades de Bogotá
   - ✅ Estado inicial: `pendiente_visita`
   - ✅ Programación de primera visita (`fecha_primera_visita`)
   - ✅ Creación automática de `VisitaTecnica` con estado `agendada`
   - ✅ Envío de correo de notificación
   - ✅ Registro de convivientes del hogar

2. **Activación de Hogar** (`activar_hogar`)
   - ✅ Formulario de evaluación completo
   - ✅ Validación de capacidad (12-15 niños)
   - ✅ Asignación de `ultima_visita`
   - ✅ Cálculo de `proxima_visita` (+365 días)
   - ✅ Estados: aprobado → `activo`, rechazado → `pendiente_visita`
   - ✅ Auto-asignación de `fecha_primera_visita` si no existe
   - ✅ Envío de correo con credenciales

3. **Registro de Visitas de Seguimiento** (`registrar_visita`)
   - ✅ Solo para hogares activos/aprobados
   - ✅ Mismo formulario de evaluación
   - ✅ Actualización de `ultima_visita` y `proxima_visita`
   - ✅ Cambio de estado si no aprueba (activo → rechazado)

4. **Dashboard de Hogares** (`hogares_dashboard`)
   - ✅ Agrupación por localidad (Bogotá - Localidad)
   - ✅ Filtros por localidad y estado
   - ✅ Botones contextuales según estado
   - ✅ Badges de estado correctos

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### 🔴 CRÍTICOS (Requieren corrección inmediata)

#### 1. **Inconsistencia en Campos de Capacidad**
**Problema:** Existen 3 campos diferentes para capacidad:
- `capacidad` (usado en activar_hogar/registrar_visita)
- `capacidad_maxima` (definido en modelo como default=15)
- `capacidad_calculada` (campo separado en modelo)

**Ubicación:** `core/models.py` líneas 306-350
```python
capacidad_maxima = models.IntegerField(default=15, ...)
capacidad_calculada = models.IntegerField(null=True, blank=True, ...)
# ⚠️ Falta campo 'capacidad' que se usa en las vistas
```

**Impacto:** 
- Error al guardar hogar.capacidad en activar_hogar (línea 5703)
- Inconsistencia en qué campo representa la capacidad real

**Solución:** Unificar en un solo campo `capacidad` o aclarar uso de cada uno.

---

#### 2. **Falta Modelo VisitaTecnica Completo**
**Problema:** Se crea `VisitaTecnica` en crear_madre pero el modelo puede no estar completo.

**Verificar:** ¿Existe el modelo con estos campos?
- fecha_programada
- tipo_visita ('V1', 'V2')
- estado ('agendada', 'realizada', 'cancelada')
- correo_enviado
- fecha_envio_correo
- observaciones_agenda

**Solución:** Revisar modelo VisitaTecnica y asegurar campos requeridos.

---

#### 3. **Programar Visita No Actualiza fecha_primera_visita**
**Problema:** La vista `programar_visita` (línea 5293) solo crea `VisitaTecnica` pero NO actualiza `hogar.fecha_primera_visita`.

**Impacto:** 
- Si se programa visita después de crear hogar, queda desincronizado
- Dashboard puede mostrar información incorrecta

**Solución:** Agregar en programar_visita:
```python
if not hogar.fecha_primera_visita:
    hogar.fecha_primera_visita = fecha_programada.date()
    hogar.save()
```

---

### 🟡 ADVERTENCIAS (Pueden causar confusión)

#### 4. **Estados del Hogar Duplicados/Confusos**
**Problema:** Muchos estados legacy sin uso claro:
```python
'pendiente_revision', 'en_revision', 'aprobado', 'rechazado', 
'en_mantenimiento', 'pendiente_visita', 'visita_agendada', 
'en_evaluacion', 'activo', 'inactivo'
```

**Uso Real:**
- `pendiente_visita` → Hogar nuevo, esperando primera visita
- `activo` → Hogar aprobado operando
- `aprobado` → ¿Igual que activo?
- `rechazado` → No pasó evaluación

**Recomendación:** 
- Simplificar a: `pendiente_visita`, `activo`, `rechazado`, `suspendido`
- Documentar claramente cada estado

---

#### 5. **Formulario de Activación Reutilizado para Seguimiento**
**Problema:** Se usa el mismo formulario para:
- Primera activación (hogar nuevo)
- Visitas de seguimiento (hogar activo)

**Ubicación:** `templates/admin/formulario_activacion_hogar.html`

**Pros:** Evita duplicación
**Cons:** Puede confundir si no se diferencia claramente (ya parcialmente resuelto con flag `es_seguimiento`)

**Estado:** ✅ Resuelto con header diferente (morado vs naranja)

---

#### 6. **Falta Validación de Fecha de Primera Visita**
**Problema:** No se valida que `fecha_primera_visita` no sea en el pasado al crear hogar.

**Ubicación:** `core/views.py` línea ~700 en crear_madre

**Solución:** Agregar validación:
```python
if fecha_primera_visita:
    fecha_visita_obj = datetime.strptime(fecha_primera_visita, '%Y-%m-%d').date()
    if fecha_visita_obj < date.today():
        messages.error(request, 'La fecha de primera visita no puede ser en el pasado.')
        return ...
```

---

### 🔵 MEJORAS RECOMENDADAS

#### 7. **Historial de Visitas**
**Faltante:** No hay registro histórico de todas las visitas.

**Actual:** 
- Solo se guarda `ultima_visita` (sobrescribe)
- `observaciones_visita` se sobrescribe también

**Recomendación:** Usar modelo `VisitaTecnica` + `ActaVisitaTecnica` para:
- Mantener historial completo
- Permitir consulta de evaluaciones anteriores
- Generar reportes de evolución del hogar

---

#### 8. **Notificaciones de Visitas Próximas**
**Faltante:** No hay sistema de recordatorios automáticos.

**Recomendación:** 
- Tarea programada (celery/scheduler) que envíe correos:
  - 7 días antes de `proxima_visita`
  - 1 día antes de `proxima_visita`
  - Día de la visita si no se ha registrado

---

#### 9. **Validación de Localidad-Dirección**
**Faltante:** No se valida que la dirección corresponda a la localidad seleccionada.

**Ejemplo:** Hogar en "Usaquén" con dirección en "Suba"

**Recomendación:** Agregar validación en `HogarForm.clean()`:
```python
def clean(self):
    cleaned_data = super().clean()
    direccion = cleaned_data.get('direccion')
    localidad = cleaned_data.get('localidad_bogota')
    
    # Validar que dirección mencione la localidad
    if localidad and direccion:
        if localidad.nombre.lower() not in direccion.lower():
            self.add_error('direccion', 
                f'La dirección debe corresponder a {localidad.nombre}')
    
    return cleaned_data
```

---

#### 10. **Capacidad vs Niños Inscritos**
**Faltante:** No hay validación de que niños activos ≤ capacidad.

**Recomendación:** 
- Al inscribir niño, verificar espacio disponible
- Dashboard mostrar: "12/15 niños" (capacidad usada/total)
- Alerta si se excede capacidad

---

## 📋 FLUJO COMPLETO DOCUMENTADO

### Ciclo de Vida de un Hogar

```
1. CREACIÓN (crear_madre)
   ├─> Estado: pendiente_visita
   ├─> fecha_primera_visita programada (opcional)
   ├─> VisitaTecnica creada (estado: agendada)
   └─> Correo enviado a madre

2. PRIMERA VISITA (activar_hogar)
   ├─> Formulario de evaluación
   ├─> Asignación de capacidad (12-15)
   ├─> ultima_visita = hoy
   ├─> proxima_visita = hoy + 365 días
   └─> Estado según resultado:
       ├─> aprobado → activo (+ correo con credenciales)
       ├─> aprobado_condiciones → activo (+ advertencia)
       ├─> no_aprobado → pendiente_visita
       └─> requiere_nueva_visita → pendiente_visita

3. OPERACIÓN NORMAL (estado: activo)
   ├─> Inscripción de niños
   ├─> Gestión diaria
   └─> Espera próxima visita

4. VISITA DE SEGUIMIENTO (registrar_visita)
   ├─> Cada 365 días (proxima_visita)
   ├─> Mismo formulario de evaluación
   ├─> Actualiza ultima_visita y proxima_visita
   └─> Estado según resultado:
       ├─> aprobado → continúa activo
       ├─> aprobado_condiciones → continúa activo (alerta)
       ├─> no_aprobado → rechazado
       └─> requiere_nueva_visita → activo (visita en 30 días)

5. ESTADOS FINALES
   ├─> activo: Operando normalmente
   ├─> rechazado: Cerrado por incumplimiento
   └─> inactivo: Cerrado voluntariamente
```

---

## 🔧 ACCIONES REQUERIDAS

### Prioridad ALTA
1. [ ] Unificar campos de capacidad (capacidad vs capacidad_maxima vs capacidad_calculada)
2. [ ] Actualizar fecha_primera_visita en programar_visita
3. [ ] Validar fecha_primera_visita no esté en el pasado

### Prioridad MEDIA
4. [ ] Simplificar estados del hogar (documentar cada uno)
5. [ ] Agregar validación localidad-dirección
6. [ ] Implementar control de capacidad vs niños inscritos

### Prioridad BAJA
7. [ ] Sistema de notificaciones automáticas
8. [ ] Historial completo de visitas
9. [ ] Dashboard con métricas de capacidad

---

## ✅ CORRECCIONES RECIENTES EXITOSAS

1. ✅ Asignación de localidades a hogares existentes
2. ✅ Dashboard agrupa por "Ciudad - Localidad"
3. ✅ Botón "Registrar Visita" funcional para hogares activos
4. ✅ Auto-asignación de fecha_primera_visita si falta
5. ✅ Corrección de hogares activos sin ultima_visita

---

## 📊 RESUMEN

**Total de problemas identificados:** 10
- 🔴 Críticos: 3
- 🟡 Advertencias: 3
- 🔵 Mejoras: 4

**Estado general del sistema:** 🟢 FUNCIONAL con mejoras recomendadas

**Próximos pasos sugeridos:**
1. Corregir campos de capacidad (crítico)
2. Actualizar programar_visita (crítico)
3. Validar fechas (advertencia)
4. Implementar mejoras según prioridad
