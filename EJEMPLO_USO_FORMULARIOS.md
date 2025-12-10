# 📘 Guía de Uso - Formularios de Dos Fases

## 🎯 Resumen del Sistema

Se han creado **3 nuevos formularios** para implementar el sistema de dos fases:

1. **HogarFormulario1Form** - Registro inicial
2. **ConvivienteFormSet** - Personas que viven en el hogar
3. **HogarFormulario2Form** - Visita técnica

---

## 📋 1. HogarFormulario1Form

### Propósito
Crear el registro inicial del hogar con datos básicos y programar la primera visita.

### Campos Incluidos
- **Ubicación**: Regional, Ciudad, Localidad (Bogotá), Dirección, Barrio
- **Identificación**: Nombre del hogar
- **Visita**: Fecha programada para la primera visita técnica

### Características Especiales
- ✅ Establece automáticamente `estado = 'pendiente_revision'`
- ✅ Marca `formulario_completo = False`
- ✅ Valida que hogares en Bogotá tengan localidad seleccionada
- ✅ Carga dinámica de ciudades según regional

### Ejemplo de Uso en Vista

```python
from django.forms import inlineformset_factory
from core.forms import HogarFormulario1Form, ConvivienteForm
from core.models import HogarComunitario, ConvivienteHogar

def crear_hogar_formulario1(request):
    """
    Vista para crear el registro inicial del hogar (Formulario 1)
    """
    # Crear el formset para convivientes
    ConvivienteFormSet = inlineformset_factory(
        HogarComunitario,
        ConvivienteHogar,
        form=ConvivienteForm,
        extra=1,  # Mínimo 1 conviviente
        can_delete=True,
        validate_min=True,
        min_num=1
    )
    
    if request.method == 'POST':
        form = HogarFormulario1Form(request.POST)
        
        if form.is_valid():
            hogar = form.save(commit=False)
            # El estado y formulario_completo ya se establecen en form.save()
            hogar.save()
            
            # Crear formset para convivientes
            formset = ConvivienteFormSet(request.POST, request.FILES, instance=hogar)
            
            if formset.is_valid():
                formset.save()
                
                messages.success(
                    request,
                    f'Hogar "{hogar.nombre_hogar}" registrado exitosamente. '
                    f'Visita programada para: {hogar.fecha_primera_visita}. '
                    f'Estado: Pendiente de Revisión.'
                )
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Error al guardar los convivientes.')
        else:
            formset = ConvivienteFormSet(instance=None)
            messages.error(request, 'Por favor corrija los errores del formulario.')
    else:
        form = HogarFormulario1Form()
        formset = ConvivienteFormSet(instance=None)
    
    context = {
        'form': form,
        'formset': formset,
        'titulo': 'Registro Inicial de Hogar Comunitario'
    }
    return render(request, 'admin/hogar_formulario1.html', context)
```

---

## 👥 2. ConvivienteFormSet

### Propósito
Registrar las personas que viven en el hogar, incluyendo certificados de antecedentes.

### Campos por Conviviente
- Tipo de documento (CC, TI, CE, PA, RC)
- Número de documento
- Nombre completo
- Parentesco con el agente educativo
- **Certificado de antecedentes (PDF)** - OBLIGATORIO

### Validaciones
- ✅ No permite documentos duplicados entre convivientes
- ✅ Valida formato del número de documento (sin puntos ni espacios)
- ✅ Requiere certificado de antecedentes en PDF

### Ejemplo de Template

```html
<!-- Tabla de convivientes -->
<h3>Personas que viven en el hogar</h3>
<table class="table table-bordered">
    <thead>
        <tr>
            <th>Tipo Doc.</th>
            <th>Número</th>
            <th>Nombre Completo</th>
            <th>Parentesco</th>
            <th>Antecedentes (PDF)</th>
            <th>Eliminar</th>
        </tr>
    </thead>
    <tbody id="convivientes-table">
        {{ formset.management_form }}
        {% for form in formset %}
        <tr>
            <td>{{ form.tipo_documento }}</td>
            <td>{{ form.numero_documento }}</td>
            <td>{{ form.nombre_completo }}</td>
            <td>{{ form.parentesco }}</td>
            <td>{{ form.antecedentes_pdf }}</td>
            <td>{{ form.DELETE }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<button type="button" id="add-conviviente" class="btn btn-secondary">
    ➕ Agregar Conviviente
</button>
```

---

## 🏠 3. HogarFormulario2Form

### Propósito
Completar la información del hogar después de realizar la visita técnica física.

### Campos Incluidos
- **Características físicas**: Estrato, habitaciones, baños, material, riesgos
- **Área social (m²)**: OBLIGATORIO, mínimo 24 m²
- **Fotos**: Interior (mín. 3) y exterior (mín. 1)
- **Geolocalización**: Latitud y longitud
- **Documentos**: Tipo de tenencia y PDF de soporte

### Validaciones Especiales

#### 1. Área Mínima (24 m²)
```python
def clean_area_social_m2(self):
    area = self.cleaned_data.get('area_social_m2')
    
    if area is None:
        raise forms.ValidationError('⚠️ El área social es OBLIGATORIA')
    
    if area < 24:
        raise forms.ValidationError(
            f'⚠️ El área debe ser de al menos 24 m². '
            f'Área ingresada: {area} m² NO CUMPLE. '
            f'El hogar NO PUEDE SER APROBADO.'
        )
    
    return area
```

#### 2. Cálculo Automático de Capacidad
```python
# Fórmula: piso(m² / 2)
# Ejemplo: 30 m² → capacidad = 15 niños
# Máximo permitido: 15 niños

if area_social_m2:
    import math
    capacidad = math.floor(area_social_m2 / 2)
    capacidad_calculada = min(capacidad, 15)  # Límite 15
```

### Tabla de Capacidades por Área

| Área (m²) | Capacidad Calculada | Estado Posible |
|-----------|---------------------|----------------|
| < 24 m² | ❌ NO APROBABLE | RECHAZADO |
| 24 - 25.9 m² | 12 niños | Aprobado |
| 26 - 27.9 m² | 13 niños | Aprobado |
| 28 - 29.9 m² | 14 niños | Aprobado |
| ≥ 30 m² | 15 niños (máximo) | Aprobado |

### Ejemplo de Uso en Vista

```python
def completar_hogar_formulario2(request, hogar_id):
    """
    Vista para completar la visita técnica (Formulario 2)
    Solo accesible si el hogar está en estado 'pendiente_revision' o 'en_revision'
    """
    hogar = get_object_or_404(HogarComunitario, pk=hogar_id)
    
    # Verificar que no esté ya completado
    if hogar.formulario_completo:
        messages.warning(request, 'Este hogar ya tiene el formulario técnico completo.')
        return redirect('detalle_hogar', hogar_id=hogar.id)
    
    # Verificar que tenga fecha de visita
    if not hogar.fecha_primera_visita:
        messages.error(request, 'Debe programar una visita antes de completar el formulario técnico.')
        return redirect('editar_hogar_form1', hogar_id=hogar.id)
    
    if request.method == 'POST':
        form = HogarFormulario2Form(request.POST, request.FILES, instance=hogar)
        
        if form.is_valid():
            hogar_actualizado = form.save()  # Auto-calcula capacidad y cambia estado a 'en_revision'
            
            messages.success(
                request,
                f'✅ Formulario técnico completado. '
                f'Área: {hogar_actualizado.area_social_m2} m². '
                f'Capacidad calculada: {hogar_actualizado.capacidad_calculada} niños. '
                f'Estado: En Revisión.'
            )
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Por favor corrija los errores.')
    else:
        form = HogarFormulario2Form(instance=hogar)
    
    context = {
        'form': form,
        'hogar': hogar,
        'titulo': f'Visita Técnica - {hogar.nombre_hogar}'
    }
    return render(request, 'admin/hogar_formulario2.html', context)
```

---

## 🔄 Flujo Completo del Sistema

### 1. Registro Inicial (Formulario 1)

```
Usuario completa Formulario 1:
├── Datos de ubicación (regional, ciudad, dirección)
├── Nombre del hogar
├── Fecha de visita programada
└── Convivientes (con PDFs de antecedentes)
    ↓
Estado: pendiente_revision
formulario_completo: False
```

### 2. Visita Técnica (Formulario 2)

```
Después de realizar la visita física:
├── Características del inmueble
├── Área social (≥24 m²) ⚠️ CRÍTICO
├── Fotos (3+ interior, 1+ exterior)
├── Geolocalización
└── Documentos de tenencia
    ↓
Cálculo automático: capacidad = piso(área/2)
Estado: en_revision
formulario_completo: True
```

### 3. Revisión Final

```
Administrador revisa el hogar completo:
├── Si área < 24 m² → RECHAZAR (no cumple mínimo)
├── Si todo correcto → APROBAR
└── Si necesita cambios → SOLICITAR CORRECCIONES
    ↓
Estado final: aprobado / rechazado
```

---

## 🚨 Validaciones Importantes

### ❌ No se puede aprobar si:
1. Área social < 24 m²
2. Faltan fotos (mínimo 3 interior + 1 exterior)
3. No hay certificados de antecedentes de convivientes
4. Formulario 2 no está completo (`formulario_completo = False`)

### ✅ Aprobación exitosa requiere:
1. Área social ≥ 24 m²
2. Mínimo 3 fotos interior + 1 foto exterior
3. Todos los convivientes con antecedentes PDF
4. Ambos formularios completados
5. Revisión administrativa aprobada

---

## 📊 Estados del Hogar

| Estado | Descripción | Formulario 1 | Formulario 2 |
|--------|-------------|--------------|--------------|
| `pendiente_revision` | Registro inicial creado | ✅ Completo | ❌ Pendiente |
| `en_revision` | Visita técnica completada | ✅ Completo | ✅ Completo |
| `aprobado` | Hogar aprobado | ✅ Completo | ✅ Completo |
| `rechazado` | Hogar rechazado | ✅ Completo | ✅/❌ Variable |

---

## 🎨 Ejemplo de Template Completo (Formulario 1)

```html
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h2>{{ titulo }}</h2>
    <p class="text-muted">Complete los datos iniciales del hogar y programe la primera visita técnica.</p>
    
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        
        <!-- Sección 1: Ubicación -->
        <div class="card mb-3">
            <div class="card-header bg-primary text-white">
                📍 Ubicación del Hogar
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        {{ form.regional.label_tag }}
                        {{ form.regional }}
                        {{ form.regional.errors }}
                    </div>
                    <div class="col-md-6">
                        {{ form.ciudad.label_tag }}
                        {{ form.ciudad }}
                        {{ form.ciudad.errors }}
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-md-6">
                        {{ form.localidad_bogota.label_tag }}
                        {{ form.localidad_bogota }}
                        {{ form.localidad_bogota.errors }}
                    </div>
                    <div class="col-md-6">
                        {{ form.barrio.label_tag }}
                        {{ form.barrio }}
                        {{ form.barrio.errors }}
                    </div>
                </div>
                <div class="row mt-3">
                    <div class="col-md-12">
                        {{ form.direccion.label_tag }}
                        {{ form.direccion }}
                        {{ form.direccion.errors }}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Sección 2: Identificación -->
        <div class="card mb-3">
            <div class="card-header bg-success text-white">
                🏠 Identificación del Hogar
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        {{ form.nombre_hogar.label_tag }}
                        {{ form.nombre_hogar }}
                        {{ form.nombre_hogar.errors }}
                    </div>
                    <div class="col-md-4">
                        {{ form.fecha_primera_visita.label_tag }}
                        {{ form.fecha_primera_visita }}
                        {{ form.fecha_primera_visita.errors }}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Sección 3: Convivientes -->
        <div class="card mb-3">
            <div class="card-header bg-info text-white">
                👥 Personas que viven en el hogar
            </div>
            <div class="card-body">
                {{ formset.management_form }}
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Tipo Doc.</th>
                            <th>Número</th>
                            <th>Nombre Completo</th>
                            <th>Parentesco</th>
                            <th>Antecedentes (PDF)</th>
                            <th>❌</th>
                        </tr>
                    </thead>
                    <tbody id="convivientes-table">
                        {% for form in formset %}
                        <tr>
                            <td>{{ form.tipo_documento }}</td>
                            <td>{{ form.numero_documento }}</td>
                            <td>{{ form.nombre_completo }}</td>
                            <td>{{ form.parentesco }}</td>
                            <td>{{ form.antecedentes_pdf }}</td>
                            <td>{{ form.DELETE }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <button type="button" class="btn btn-secondary" id="add-conviviente">
                    ➕ Agregar Conviviente
                </button>
            </div>
        </div>
        
        <!-- Botones -->
        <div class="text-end">
            <a href="{% url 'admin_dashboard' %}" class="btn btn-secondary">Cancelar</a>
            <button type="submit" class="btn btn-primary">💾 Guardar Registro Inicial</button>
        </div>
    </form>
</div>

<script>
// Script para agregar convivientes dinámicamente
document.getElementById('add-conviviente').addEventListener('click', function() {
    const table = document.getElementById('convivientes-table');
    const totalForms = document.querySelector('[name$="TOTAL_FORMS"]');
    const formCount = parseInt(totalForms.value);
    
    // Clonar la última fila
    const lastRow = table.querySelector('tr:last-child');
    const newRow = lastRow.cloneNode(true);
    
    // Actualizar los IDs y names
    newRow.innerHTML = newRow.innerHTML.replace(
        new RegExp(`form-(\\d+)-`, 'g'),
        `form-${formCount}-`
    );
    
    // Limpiar valores
    newRow.querySelectorAll('input, select').forEach(input => {
        if (input.type !== 'checkbox') input.value = '';
    });
    
    table.appendChild(newRow);
    totalForms.value = formCount + 1;
});
</script>
{% endblock %}
```

---

## ✅ Próximos Pasos de Implementación

### Fase 2 ✅ COMPLETADA
- [x] HogarFormulario1Form creado
- [x] ConvivienteFormSet creado
- [x] HogarFormulario2Form creado
- [x] Validación de área ≥24m²
- [x] Cálculo automático de capacidad

### Fase 3 - Crear Vistas (SIGUIENTE)
- [ ] Vista: `crear_hogar_formulario1()`
- [ ] Vista: `editar_hogar_formulario1()`
- [ ] Vista: `completar_hogar_formulario2()`
- [ ] Vista: `lista_hogares_pendientes()`
- [ ] Vista: `aprobar_rechazar_hogar()`

### Fase 4 - Crear Templates (SIGUIENTE)
- [ ] Template: `hogar_formulario1.html`
- [ ] Template: `hogar_formulario2.html`
- [ ] Template: `lista_hogares_revision.html`
- [ ] Template: `detalle_hogar_completo.html`

### Fase 5 - Validaciones Adicionales
- [ ] Validar mínimo 3 fotos interior
- [ ] Validar mínimo 1 foto exterior
- [ ] Validar PDFs de antecedentes presentes

### Fase 6 - Sistema de Alertas
- [ ] Alerta de visitas próximas (7 días antes)
- [ ] Alerta de visitas vencidas
- [ ] Alerta de visitas anuales

---

## 📞 Soporte

Para más información sobre el sistema de dos fases, consulte:
- `REESTRUCTURACION_HOGARES.md` - Documentación completa del sistema
- `core/models.py` - Modelos actualizados con nuevos campos
- `core/forms.py` - Formularios implementados
