# 🏠 REESTRUCTURACIÓN DEL SISTEMA DE HOGARES COMUNITARIOS

## 📋 RESUMEN EJECUTIVO

Se divide la creación de hogares en DOS formularios separados para mejorar el flujo de trabajo y cumplir con el proceso real de habilitación del ICBF.

---

## 🔄 FLUJO COMPLETO DEL SISTEMA

```
FORMULARIO 1              VALIDACIÓN           FORMULARIO 2
(Registro Inicial)  →  (Visita Técnica)  →  (Habilitación Final)
```

---

## 📝 FORMULARIO 1 - REGISTRO INICIAL DEL HOGAR

### Objetivo
Crear el registro básico del hogar y agendar la primera visita técnica.

### Campos Obligatorios

#### 1. Ubicación del Hogar
- ✅ Regional (obligatorio)
- ✅ Ciudad (obligatorio)
- ✅ Localidad (obligatorio si es Bogotá)
- ✅ Dirección Completa (obligatorio)
- ✅ Barrio (opcional)

#### 2. Datos Básicos del Hogar
- ✅ Nombre del Hogar Comunitario (obligatorio, único)
- ✅ **Fecha de Primera Visita Técnica** (obligatorio, ≥ hoy)
- ✅ Capacidad Máxima Tentativa: **15 niños** (fijo, no editable)
- ✅ Estado: **"Pendiente de Revisión"** (automático, no editable)

#### 3. Datos del Agente Educativo (Madre Comunitaria)
- ✅ Tipo de Documento
- ✅ Número de Documento (validación de duplicados en tiempo real)
- ✅ Nombres
- ✅ Apellidos
- ✅ Información Académica (educación/certificaciones)

#### 4. Personas que Viven en el Hogar
**Tabla Repetible** (mínimo 1 registro obligatorio):
- Tipo de Documento
- Número de Documento
- Nombre Completo
- Parentesco (Ej: Madre, Esposo, Hijo, etc.)
- **Archivo PDF de Antecedentes Penales** (obligatorio)

### Estado Resultante
- Hogar creado con estado: `pendiente_revision`
- Visible en panel "Hogares Pendientes de Revisión"
- Fecha de visita programada y visible

---

## 🏥 FORMULARIO 2 - VISITA TÉCNICA Y VALIDACIÓN

### Cuándo se Desbloquea
- ✅ Después de que ocurrió la visita programada
- ✅ O cuando el administrador entra a "Completar Revisión del Hogar"

### Campos del Formulario 2

#### 1. Características Físicas del Inmueble
- Número de Habitaciones
- Número de Baños  
- Material de Construcción (textarea)
- Riesgos Cercanos al Hogar (textarea)

#### 2. Área Social y Capacidad (¡NUEVO!)
- **Metros Cuadrados del Área Social** (obligatorio)
  - Campo numérico con 2 decimales
  - Mínimo: 24 m²
  
- **Capacidad Calculada Automáticamente**
  ```
  Fórmula: floor(área_m2 / 2)
  
  Reglas:
  - < 24 m²     → HOGAR NO APTO (rechazar)
  - 24-29.9 m²  → Apto para 12-14 niños
  - ≥ 30 m²     → Apto para 15 niños (máximo)
  ```

#### 3. Tenencia del Inmueble
- Tipo de Tenencia (Propio/Arriendo/Comodato)
- Documento Soporte PDF (obligatorio)

#### 4. Geolocalización
- Latitud (opcional, Google Maps)
- Longitud (opcional, Google Maps)

#### 5. Fotos del Hogar
**Fotos Interiores** (mínimo 3 obligatorias):
- Sala/Área Social
- Baño
- Habitación

**Fotos Exteriores** (mínimo 1 obligatoria):
- Fachada del hogar

#### 6. Decisión Final
Después de la visita, el estado cambia a:
- ✅ **Aprobado** (si cumple todos los requisitos)
- ❌ **Rechazado** (si no cumple área mínima o condiciones)
- 🔧 **En Mantenimiento** (si requiere mejoras)

### Validaciones Automáticas
- Si área < 24 m² → No permitir aprobar
- Si fotos < 3 interior → No permitir aprobar
- Si fotos < 1 exterior → No permitir aprobar
- Documento de tenencia obligatorio

---

## 📊 NUEVOS ESTADOS DEL HOGAR

| Estado | Descripción |
|--------|-------------|
| `pendiente_revision` | Hogar recién creado (Formulario 1 completado) |
| `en_revision` | Visita técnica en proceso (Formulario 2 iniciado) |
| `aprobado` | Hogar habilitado para operar |
| `rechazado` | Hogar no cumple requisitos |
| `en_mantenimiento` | Hogar requiere mejoras |

---

## 🗄️ CAMBIOS EN LA BASE DE DATOS

### Modelo: `HogarComunitario`

#### Nuevos Campos
```python
fecha_primera_visita = DateField()           # Fecha programada de visita
area_social_m2 = DecimalField()              # Área en metros cuadrados
capacidad_calculada = IntegerField()         # Calculada automáticamente
formulario_completo = BooleanField()         # True si Formulario 2 completado
```

#### Estados Actualizados
```python
choices = [
    ('pendiente_revision', 'Pendiente de Revisión'),
    ('en_revision', 'En Revisión'),
    ('aprobado', 'Aprobado'),
    ('rechazado', 'Rechazado'),
    ('en_mantenimiento', 'En Mantenimiento'),
]
default = 'pendiente_revision'
```

### Modelo: `ConvivienteHogar`

#### Campos Actualizados
```python
tipo_documento = CharField(choices=[CC, TI, CE, PA, RC])
numero_documento = CharField(max_length=20)
nombre_completo = CharField(max_length=200)
parentesco = CharField(max_length=50)
antecedentes_pdf = FileField()               # PDF de antecedentes penales
fecha_registro = DateTimeField()
```

---

## 🎯 MÓDULO DE GESTIÓN DE HOGARES

### Panel Principal
Debe mostrar hogares filtrados por estado:
- Pendiente de Revisión
- En Revisión
- Aprobados
- Rechazados
- En Mantenimiento

### Funcionalidades
- ✅ Filtros por localidad
- ✅ Buscador por nombre de hogar
- ✅ Fecha de visitas próximas
- ✅ Alertas automáticas (1 semana antes de visita)

---

## 📅 MÓDULO DE VISITAS TÉCNICAS

### Requisitos
- Mínimo 1 visita anual obligatoria
- Historial de visitas por hogar
- Fechas programadas visibles

### Alertas Automáticas
- 🔴 Visita vencida (pasó la fecha)
- 🟡 Visita cercana (< 7 días)
- ⚠️ Sin visita programada del año actual

---

## 👨‍👩‍👧 DASHBOARD DEL PADRE (MEJORAS)

### Nuevas Funcionalidades

#### Ver Hogares
- Listado completo de hogares disponibles
- Filtros por localidad
- Información visible:
  - Agente educativo a cargo
  - Capacidad aprobada
  - Dirección
  - Fotos del hogar
  - Lista de niños inscritos

#### Información del Niño
- Documentación completa
- Historial de asistencia
- Gráficas de asistencia

### Gráficas del Dashboard
1. Total de hogares registrados
2. Hogares activos vs inactivos
3. Hogares pendientes vs aprobados
4. Próximas visitas programadas
5. % de hogares con visitas vencidas

---

## 🔧 PLAN DE IMPLEMENTACIÓN

### Fase 1: Base de Datos ✅
- [x] Modificar modelo `HogarComunitario`
- [x] Modificar modelo `ConvivienteHogar`
- [ ] Crear y ejecutar migraciones

### Fase 2: Formularios
- [ ] Crear `HogarFormulario1` (registro inicial)
- [ ] Crear `HogarFormulario2` (visita técnica)
- [ ] Crear `ConvivienteFormSet` (tabla repetible)

### Fase 3: Vistas
- [ ] Vista para Formulario 1
- [ ] Vista para Formulario 2
- [ ] Vista panel "Pendientes de Revisión"
- [ ] Vista "Completar Revisión"

### Fase 4: Templates
- [ ] Template Formulario 1
- [ ] Template Formulario 2
- [ ] Template panel de gestión
- [ ] Template dashboard padre mejorado

### Fase 5: Validaciones
- [ ] Validación área mínima (24 m²)
- [ ] Cálculo automático de capacidad
- [ ] Validación de fotos mínimas
- [ ] Validación de fecha de visita

### Fase 6: Alertas y Notificaciones
- [ ] Sistema de alertas de visitas
- [ ] Correos automáticos de recordatorio
- [ ] Notificaciones dashboard

---

## 📝 NOTAS IMPORTANTES

1. **Retrocompatibilidad**: Los estados legacy se mantienen para hogares antiguos
2. **Migración de Datos**: Los hogares existentes necesitarán:
   - Asignar estado apropiado
   - Completar campos nuevos si están activos
3. **Campos Legacy**: Se mantienen `nombre`, `cedula`, `edad` en ConvivienteHogar por compatibilidad

---

## 🚀 PRÓXIMOS PASOS

1. Ejecutar migraciones
2. Crear formularios separados
3. Implementar vistas
4. Actualizar templates
5. Pruebas de flujo completo
6. Migrar datos existentes
7. Capacitación usuarios

---

**Fecha de Creación**: 9 de diciembre de 2025  
**Versión**: 1.0
