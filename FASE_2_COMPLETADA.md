# ✅ FASE 2 COMPLETADA - Formularios Separados Creados

## 📋 Resumen de Implementación

Se han creado **3 nuevos formularios** para el sistema de dos fases:

---

## 🎯 1. HogarFormulario1Form
**Ubicación:** `core/forms.py` (líneas ~965-1050)

### Características:
- ✅ Formulario de registro inicial del hogar
- ✅ Solo incluye campos básicos:
  - Regional, Ciudad, Localidad (Bogotá)
  - Dirección, Barrio
  - Nombre del hogar
  - **Fecha de primera visita técnica**
  
### Funcionalidad Automática:
```python
def save(self, commit=True):
    instance = super().save(commit=False)
    instance.estado = 'pendiente_revision'  # Estado inicial
    instance.formulario_completo = False    # Falta Formulario 2
    if commit:
        instance.save()
    return instance
```

### Validaciones:
- ✅ Si la ciudad es Bogotá → requiere localidad
- ✅ Carga dinámica de ciudades según regional seleccionada
- ✅ Fecha de visita mínima: 2025-01-01 (no permite fechas pasadas)

---

## 👥 2. ConvivienteFormSet + ConvivienteForm
**Ubicación:** `core/forms.py` (líneas ~1053-1120)

### Características:
- ✅ FormSet para agregar múltiples convivientes
- ✅ Incluye campos:
  - Tipo de documento (CC, TI, CE, PA, RC)
  - Número de documento
  - Nombre completo
  - Parentesco con el agente educativo
  - **Certificado de antecedentes (PDF) - OBLIGATORIO**

### Validaciones Especiales:
```python
def clean(self):
    # No permite documentos duplicados entre convivientes
    documentos = []
    for form in self.forms:
        documento = form.cleaned_data.get('numero_documento')
        if documento in documentos:
            raise ValidationError('Documento duplicado')
        documentos.append(documento)
```

```python
def clean_numero_documento(self):
    # Limpia espacios, puntos y comas del documento
    documento = documento.replace(' ', '').replace('.', '').replace(',', '')
    return documento
```

### Uso Recomendado:
```python
from django.forms import inlineformset_factory

ConvivienteFormSet = inlineformset_factory(
    HogarComunitario,
    ConvivienteHogar,
    form=ConvivienteForm,
    extra=1,        # Mínimo 1 conviviente
    can_delete=True,
    validate_min=True,
    min_num=1
)
```

---

## 🏠 3. HogarFormulario2Form
**Ubicación:** `core/forms.py` (líneas ~1123-1320)

### Características:
- ✅ Formulario de visita técnica (se completa después de la visita física)
- ✅ Incluye campos:
  - Estrato, habitaciones, baños
  - Material de construcción
  - Riesgos cercanos
  - **Área social (m²) - OBLIGATORIO ≥24m²**
  - Fotos interior/exterior
  - Geolocalización (latitud/longitud)
  - Tipo de tenencia y documento PDF

### 🚨 Validación Crítica de Área:
```python
def clean_area_social_m2(self):
    area = self.cleaned_data.get('area_social_m2')
    
    if area is None:
        raise ValidationError('⚠️ El área social es OBLIGATORIA')
    
    if area < 24:
        raise ValidationError(
            f'⚠️ El área debe ser de al menos 24 m². '
            f'Área ingresada: {area} m² NO CUMPLE. '
            f'El hogar NO PUEDE SER APROBADO.'
        )
    
    return area
```

### 🧮 Cálculo Automático de Capacidad:
```python
def save(self, commit=True):
    instance = super().save(commit=False)
    
    if instance.area_social_m2:
        import math
        capacidad = math.floor(instance.area_social_m2 / 2)
        instance.capacidad_calculada = min(capacidad, 15)  # Máximo 15
        instance.capacidad_maxima = instance.capacidad_calculada
    
    instance.formulario_completo = True     # Marca como completo
    instance.estado = 'en_revision'         # Listo para revisión admin
    
    if commit:
        instance.save()
    return instance
```

### 📊 Tabla de Capacidades:

| Área Social | Capacidad | Estado Posible |
|-------------|-----------|----------------|
| < 24 m² | ❌ NO APROBABLE | RECHAZADO |
| 24 - 25.9 m² | 12 niños | Aprobado |
| 26 - 27.9 m² | 13 niños | Aprobado |
| 28 - 29.9 m² | 14 niños | Aprobado |
| ≥ 30 m² | 15 niños (máximo) | Aprobado |

**Fórmula:** `capacidad = piso(área_m² / 2)`, límite máximo 15 niños

---

## 📁 Archivos Modificados

### 1. `core/forms.py`
- ✅ Importado `ConvivienteHogar` en línea 5
- ✅ Agregados 3 nuevos formularios (400+ líneas de código)
- ✅ Sin errores de sintaxis (verificado con `python manage.py check`)

### 2. `EJEMPLO_USO_FORMULARIOS.md` (NUEVO)
- ✅ Guía completa de uso de los formularios
- ✅ Ejemplos de código para vistas
- ✅ Ejemplos de templates HTML
- ✅ Documentación de validaciones
- ✅ Tabla de capacidades por área
- ✅ Flujo completo del sistema

---

## 🔄 Flujo Implementado

### Paso 1: Registro Inicial
```
Usuario → HogarFormulario1Form
       → ConvivienteFormSet (con PDFs de antecedentes)
       ↓
Hogar creado:
  - estado: 'pendiente_revision'
  - formulario_completo: False
  - fecha_primera_visita: [programada]
```

### Paso 2: Visita Técnica
```
Después de la visita física:
Usuario → HogarFormulario2Form
       → Ingresa área social (≥24 m²)
       → Sube fotos (3+ interior, 1+ exterior)
       → Completa características físicas
       ↓
Hogar actualizado:
  - estado: 'en_revision'
  - formulario_completo: True
  - area_social_m2: [valor ingresado]
  - capacidad_calculada: piso(área/2)
  - capacidad_maxima: [igual a calculada]
```

### Paso 3: Revisión Administrativa
```
Administrador revisa:
  - Si área < 24m² → NO puede aprobar
  - Si todo correcto → estado = 'aprobado'
  - Si hay problemas → estado = 'rechazado'
```

---

## ✅ Verificaciones Realizadas

1. ✅ **Sintaxis:** `python manage.py check` → No issues (0 silenced)
2. ✅ **Importaciones:** `ConvivienteHogar` importado correctamente
3. ✅ **Widgets:** Corregido `FileInput` → `ClearableFileInput`
4. ✅ **Validaciones:** Implementadas validaciones de área, documentos duplicados
5. ✅ **Cálculos:** Capacidad automática con fórmula `piso(área/2)`

---

## 📝 Próximos Pasos (Fase 3)

### Crear Vistas en `core/views.py`:

1. **Vista: crear_hogar_formulario1()**
   - Maneja HogarFormulario1Form + ConvivienteFormSet
   - Guarda hogar en estado 'pendiente_revision'
   - Requiere fecha de visita

2. **Vista: completar_hogar_formulario2()**
   - Solo accesible si `formulario_completo = False`
   - Valida área ≥24m²
   - Calcula capacidad automáticamente
   - Cambia estado a 'en_revision'

3. **Vista: lista_hogares_pendientes()**
   - Lista hogares en 'pendiente_revision' (Formulario 1 completo)
   - Lista hogares en 'en_revision' (ambos formularios completos)
   - Permite filtrar por estado

4. **Vista: aprobar_rechazar_hogar()**
   - Solo administradores
   - Valida área antes de aprobar
   - Cambia estado final: 'aprobado' o 'rechazado'

5. **Vista: editar_hogar_formulario1()**
   - Permite modificar datos básicos
   - Solo si hogar no está aprobado

---

## 🎨 Próximos Pasos (Fase 4)

### Crear Templates:

1. **`templates/admin/hogar_formulario1.html`**
   - Formulario de registro inicial
   - Tabla dinámica de convivientes
   - JavaScript para agregar/eliminar filas

2. **`templates/admin/hogar_formulario2.html`**
   - Formulario de visita técnica
   - Validación en tiempo real de área
   - Mostrar capacidad calculada
   - Upload de fotos

3. **`templates/admin/lista_hogares_revision.html`**
   - Lista de hogares pendientes
   - Filtros por estado
   - Botones: Ver detalle, Completar Formulario 2, Aprobar/Rechazar

4. **`templates/admin/detalle_hogar_completo.html`**
   - Vista completa del hogar
   - Información de ambos formularios
   - Listado de convivientes
   - Fotos subidas
   - Botones de acción según estado

---

## 📊 Estado Actual del Proyecto

### ✅ Completado (Fase 1 + Fase 2):
- [x] Modelos actualizados (HogarComunitario, ConvivienteHogar)
- [x] Migración 0034 creada y aplicada
- [x] HogarFormulario1Form implementado
- [x] ConvivienteFormSet implementado
- [x] HogarFormulario2Form implementado
- [x] Validación de área ≥24m² implementada
- [x] Cálculo automático de capacidad implementado
- [x] Documentación completa creada

### ⏹️ Pendiente (Fases 3-6):
- [ ] Vistas para ambos formularios
- [ ] Templates HTML
- [ ] Sistema de alertas de visitas
- [ ] Dashboard para padres mejorado
- [ ] Validación de cantidad de fotos
- [ ] Historial de visitas anuales

---

## 🚀 Comandos de Verificación

```powershell
# Verificar no hay errores
python manage.py check

# Ver modelos actualizados
python manage.py shell
>>> from core.models import HogarComunitario, ConvivienteHogar
>>> HogarComunitario._meta.get_fields()

# Importar formularios
>>> from core.forms import HogarFormulario1Form, HogarFormulario2Form, ConvivienteForm
>>> HogarFormulario1Form.Meta.fields
>>> HogarFormulario2Form.Meta.fields
```

---

## 📞 Documentación Relacionada

- `REESTRUCTURACION_HOGARES.md` - Especificaciones completas del sistema
- `EJEMPLO_USO_FORMULARIOS.md` - Guía de uso detallada
- `core/models.py` - Modelos con nuevos campos
- `core/forms.py` - Formularios implementados (3 nuevos)

---

**Fecha de Implementación:** 9 de diciembre de 2025  
**Estado:** ✅ FASE 2 COMPLETADA  
**Próximo Paso:** Fase 3 - Crear vistas en `core/views.py`
