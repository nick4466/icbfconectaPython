# ICBF Conecta - Guía para Agentes IA

## Visión General del Proyecto
**ICBF Conecta** es una plataforma Django 5.2 para gestión integral de programas de atención a madres comunitarias e hijos en el ICBF (Instituto Colombiano de Bienestar Familiar). Integra:
- Gestión de usuarios multirrol (administrador, madre comunitaria, padre)
- Seguimiento del desarrollo infantil con evaluaciones dimensionales
- Planificación educativa y documentación
- Notificaciones y comunicaciones
- Generación de reportes en PDF
- Gestión de solicitudes (matriculación, retiro)

**Bases de datos:** SQLite (desarrollo), estructura SQL multi-tabla en `database_structure.sql`

---

## Arquitectura Clave

### Modelos Centrales (core/models.py)
```python
# Jerarquía de usuarios - base autenticación
Usuario (AbstractUser)  # User model personalizado
├── Padre
├── MadreComunitaria
└── Administrador (Usuario con rol)

# Estructura territorial (ICBF)
Regional
├── Ciudad
└── Hogares Comunitarios

# Geografía Colombia (soporte dinámico)
Departamento → Municipio → LocalidadBogota/BarrioBogota
```

**Patrón crítico:** Los formularios cargan ubicaciones **dinámicamente en cascada** (Departamento → Municipio → Localidad → Barrio via AJAX). Implementado en templates con selects que se sincronizan en `core/views.py` vía endpoints JSON.

### Apps Principales

| App | Responsabilidad |
|-----|-----------------|
| **core** | Autenticación, usuarios, geografía, validaciones técnicas |
| **planeaciones** | Diseño curricular (Dimensiones, Planeaciones, Documentación) |
| **desarrollo** | Evaluaciones infantiles multidimensionales, seguimiento diario |
| **novedades** | Eventos/incidentes reportados por madres |
| **correos** | Envío de emails, logs de comunicación |
| **asistencia** | Control de asistencia |
| **notifications** | Sistema de alertas a usuarios |

---

## Patrones y Convenciones Específicas

### 1. **Autenticación Basada en Roles Personalizado**
```python
# En core/decorators.py
@rol_requerido('madre_comunitaria')  # Decorador requerido en vistas protegidas
def mi_vista(request):
    # request.user.rol.nombre_rol verifica permisos
```
**Convención:** 
- Roles: `'administrador'`, `'madre_comunitaria'`, `'padre'` (Rol model)
- **NO usar** `@permission_required` - usar `@rol_requerido` personalizado
- `AUTH_USER_MODEL = 'core.Usuario'` en settings

### 2. **Validación de Archivos Subidos**
```python
# core/forms.py: FileSizeValidationMixin
class MiForm(FileSizeValidationMixin, forms.ModelForm):
    FILE_FIELDS = ['foto', 'cedula']  # Optional - auto-detecta si no existe
```
- Límite: 5 MB por defecto (`MAX_UPLOAD_SIZE_BYTES`)
- **No subir archivos sin mixins** - siempre validar tamaño

### 3. **Rutas de Carga de Documentos (Media)**
```python
# core/models.py
def madre_upload_path(instance, filename):
    return f"madres_documentos/{instance.usuario.documento}/{filename}"

# Jerarquía en /media:
madres_documentos/{documento}/[antecedentes, cedulas, educacion, firmas, medico, etc]
administradores/fotos/{documento}/
hogares/{id}/
ninos/{id}/
```
**Patrón:** Documentos organizados por número de cédula del usuario, no por ID.

### 4. **Evaluaciones Multidimensionales**
```python
# desarrollo/models.py
Planeacion → Documentacion (genera materiales por Dimensión)
DesarrolloNino + EvaluacionDimension → SeguimientoDiario

# Cada Dimensión de planeación puede evaluarse múltiples veces
# Las evaluaciones se guardan con estados (no se sobrescriben)
```
**Consideración:** Evaluaciones acumulativas; no eliminar históricamente.

### 5. **Generación de PDFs**
```python
# core/views.py importa xhtml2pdf
from xhtml2pdf import pisa
# Usa templates HTML → IO buffer → respuesta PDF
```
- **Dependencia:** `xhtml2pdf==0.2.17` en requirements
- Crear templates en `templates/` con CSS inline
- Return HttpResponse con `content_type='application/pdf'`

### 6. **Emails Personalizados**
```python
# correos/models.py - EmailLog registra todo
from django.core.mail import EmailMessage
msg = EmailMessage(subject, html_content, from_email, to_email)
msg.content_subtype = "html"
msg.send()
# + registrar en EmailLog para auditoría
```
- **Variables de entorno:** `.env` carga credenciales SMTP (ver `settings.py`)
- Plantillas HTML en `templates/emails/`

### 7. **Carga Dinámica Cascada (Geografía)**
```javascript
// En templates: Departamento → Municipio → Localidad → Barrio
// Endpoints en core/views.py (buscar "obtener_" o "get_municipios")
fetch('/api/municipios?departamento_id=5')
.then(r => r.json())
.then(data => populateSelect('municipio', data))
```
**Crítico:** Cada nivel depende del anterior. Si se rompe un endpoint, cascada falla.

---

## Flujos Clave de Desarrollo

### Crear una Nueva Feature de Usuario
1. Agregar campos en `core/models.py` (Usuario o app específica)
2. Crear formulario en `app/forms.py` con `FileSizeValidationMixin` si hay uploads
3. Decorar vista con `@rol_requerido('role')`
4. Template en `templates/app/`
5. URLs en `app/urls.py` + agregar path a `icbfconecta/urls.py`
6. **Migración:** `python manage.py makemigrations && migrate`

### Modificar Ubicaciones/Geografía
- **NO editar** localidades directamente sin `cargar_barrios_bogota.py`
- Revisar `SOLUCION_BARRIOS_MADRE.md` para histórico de correcciones
- Usar management commands si es necesario agregar datos masivos

### Tests
- `test_barrios.py` - verifica integridad de geografía
- Cada app tiene `tests.py` (ejemplo: verificar cascadas)
- **Ejecutar antes de merge:** `python manage.py test`

---

## Dependencias Externas Clave
- **APScheduler 3.10.4** → Tareas programadas (revisar `core/scheduler.py`)
- **reportlab** + **xhtml2pdf** → Generación PDF
- **Pillow 12.0.0** → Procesamiento imágenes
- **openpyxl** → Exportación Excel
- **python-dateutil** → Manejo de fechas

---

## Configuración Desarrollo
```bash
source venv/Scripts/Activate.ps1  # Windows PowerShell
python manage.py runserver        # Puerto 8000 por defecto
# Media files servidos desde /media (configurado en urls.py)
```
**Tarea VS Code:** `runserver-media` ejecuta el servidor (background task).

---

## Errores Comunes Evitar

| Error | Solución |
|-------|----------|
| `Acceso denegado` | Verificar `@rol_requerido` en vista y rol del usuario en admin |
| Archivos no suben | Revisar `FileSizeValidationMixin.clean()` - logs en consola |
| Cascadas geográficas vacías | Verificar endpoint en views (búsqueda por `Q()` en models) |
| PDF vacío/cortado | CSS inline solo; no cargar CSS externo en xhtml2pdf |
| Emails no llegan | Verificar `.env` SMTP settings y `EmailLog` model para debugging |

---

## Comandos Útiles
```bash
# Shell Django interactivo
python manage.py shell

# Cargar datos iniciales
python manage.py loaddata datos_iniciales.json

# Tests
python manage.py test

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superuser
python manage.py createsuperuser
```

---

## Archivos de Referencia para Contexto Profundo
- **Modelos:** [core/models.py](core/models.py) (1427 líneas - relaciones maestro)
- **Vistas:** [core/views.py](core/views.py) (7515 líneas - lógica principal)
- **Dashboard mejorado:** [core/views_dashboard.py](core/views_dashboard.py)
- **Geografía:** [core/forms.py](core/forms.py) (cascadas AJAX)
- **Decoradores:** [core/decorators.py](core/decorators.py)
- **Histórico cambios:** [REGISTRO_CAMBIOS.md](REGISTRO_CAMBIOS.md)
