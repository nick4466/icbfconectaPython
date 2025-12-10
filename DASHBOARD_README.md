# 📊 Dashboard Administrativo Completo - ICBF Conecta

## 🎯 Descripción General

Dashboard administrativo avanzado para la gestión integral del sistema ICBF Conecta, incluyendo estadísticas en tiempo real, gráficas interactivas, exploración avanzada de hogares, vistas tipo "carpetas" de niños y previsualización de documentos integrada.

---

## ✨ Características Principales

### 1. **Estadísticas en Tiempo Real**
Tarjetas informativas con métricas clave:
- 🏠 Total de hogares comunitarios activos
- 👨‍🏫 Total de agentes educativos
- 👶 Total de niños matriculados
- ⏱️ Solicitudes pendientes
- 📅 Visitas domiciliarias próximas
- ⚠️ Visitas vencidas

### 2. **Gráficas Interactivas** (Chart.js)
- 📈 **Matrículas por mes**: Gráfica de línea con últimos 6 meses
- 🥧 **Estados de hogares**: Gráfica de dona (aprobados/pendientes/revisión)
- 📊 **Top 10 hogares**: Barras horizontales con mayor matrícula
- 🎯 **Solicitudes**: Pastel de aprobadas vs rechazadas vs pendientes

Filtros disponibles: 6 meses, 1 año, todo el tiempo

### 3. **Exploración Avanzada de Hogares**
#### Vista por Localidad
- Agrupación automática de hogares por localidad
- Tarjetas visuales con información resumida
- Estadísticas por localidad (cantidad de hogares y niños)
- Búsqueda y filtros dinámicos

#### Filtros Disponibles
- 🔍 Búsqueda global (nombre, responsable, dirección)
- 📍 Por localidad
- ⚡ Por estado (aprobado, pendiente, revisión, rechazado)
- 🗓️ Por fecha de creación

### 4. **Vista Detallada de Hogar (Modal)**
Al hacer clic en un hogar se muestra:
- **Información general**: Nombre, responsable, dirección, estado
- **Estadísticas del hogar**: 
  - Capacidad utilizada (barra de progreso)
  - Total de visitas realizadas
  - Fecha de última visita
- **Vista de niños tipo carpetas**: Miniatura visual de cada niño
- **Documentos del hogar**: Lista con previsualización

### 5. **Vista Tipo "Carpetas" de Niños** 👶
Explorador visual donde cada niño aparece como tarjeta clickeable:
- **Foto/Avatar** del niño
- **Nombre completo**
- **Edad**
- **Indicador de estado** (punto verde = activo)

### 6. **Carpeta Completa del Niño**
Al abrir la carpeta de un niño:

#### Tabs Organizados:
1. **Información General**
   - Datos personales (nombre, documento, edad, género)
   - Información del hogar
   - Observaciones médicas

2. **Tutor/Familia**
   - Datos del tutor o padre/madre
   - Documento, teléfono, ocupación
   - Situación económica
   - Parentesco

3. **Documentos**
   - Registro civil
   - Carnet de vacunas
   - Certificado de salud
   - Fotografías
   - **Vista previa integrada** (sin abrir nueva ventana)

4. **Historial**
   - Timeline de eventos importantes
   - Fecha de ingreso
   - Cambios de estado
   - Observaciones históricas

### 7. **Previsualización de Documentos** 📄🖼️
**Sin salir del sistema, sin descargar archivos**

#### Documentos PDF:
- Visor integrado con iframe
- Controles de navegación del navegador
- Descarga opcional

#### Imágenes (JPG, PNG, JPEG):
- Visualización en alta calidad
- **Controles de zoom**:
  - Zoom in (+)
  - Zoom out (-)
  - Reset
  - Rotación 90°
- **Atajos de teclado**:
  - `+` / `=` → Zoom in
  - `-` → Zoom out
  - `0` → Reset zoom
  - `R` → Rotar
  - `ESC` → Cerrar
- **Zoom con rueda del mouse**

#### Aplicaciones:
- Ver constancia de residencia del hogar
- Revisar documentos del agente educativo
- Verificar certificados médicos de niños
- Consultar actas de visitas domiciliarias
- Revisar registros civiles

---

## 🗂️ Estructura de Archivos

```
icbfconectaPython/
├── core/
│   ├── views.py                    # Vistas principales (importa views_dashboard)
│   └── views_dashboard.py          # 🆕 Vistas del dashboard mejorado
│       ├── dashboard_admin()       # Dashboard principal
│       ├── hogares_dashboard()     # Gestión de hogares
│       ├── hogar_detalle_api()     # API JSON detalles de hogar
│       ├── nino_detalle_api()      # API JSON detalles de niño
│       ├── preview_document()      # Vista de previsualización
│       ├── nino_carpeta_view()     # Vista carpeta completa de niño
│       └── Funciones auxiliares    # generar_chart_*, calcular_edad, etc.
│
├── templates/
│   └── admin/
│       ├── dashboard_admin.html         # 🆕 Dashboard principal
│       ├── hogares_dashboard.html       # 🆕 Vista de gestión de hogares
│       ├── nino_carpeta.html           # 🆕 Carpeta completa del niño
│       └── preview_document.html        # 🆕 Visor de documentos
│
└── icbfconecta/
    └── urls.py                          # URLs del dashboard (actualizadas)
```

---

## 🔗 URLs Configuradas

```python
# Dashboard principal
path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin')

# Gestión de hogares
path('dashboard/admin/hogares/', views.hogares_dashboard, name='hogares_dashboard')

# APIs JSON para modales
path('api/hogares/<int:hogar_id>/detalle/', views.hogar_detalle_api, name='hogar_detalle_api')
path('api/ninos/<int:nino_id>/detalle/', views.nino_detalle_api, name='nino_detalle_api')

# Preview de documentos
path('preview/<str:tipo>/<int:id>/<str:campo>/', views.preview_document, name='preview_document')

# Carpeta del niño
path('ninos/<int:nino_id>/carpeta/', views.nino_carpeta_view, name='nino_carpeta')
```

---

## 🎨 Diseño y Estilos

### Color Palette:
```css
:root {
  --primary: #2563eb;      /* Azul principal */
  --secondary: #10b981;    /* Verde secundario */
  --danger: #ef4444;       /* Rojo */
  --warning: #f59e0b;      /* Naranja */
  --info: #06b6d4;         /* Cian */
  --dark: #1f2937;         /* Gris oscuro */
  --light: #f9fafb;        /* Gris claro */
  --border: #e5e7eb;       /* Bordes */
  --text: #374151;         /* Texto principal */
  --text-light: #6b7280;   /* Texto secundario */
}
```

### Componentes UI:
- **Sidebar fijo** con gradiente azul
- **Topbar sticky** con búsqueda global
- **Tarjetas de estadísticas** con hover effect
- **Gráficas responsivas** (Chart.js 4.4.0)
- **Modales** con overlay oscuro
- **Tablas** con hover y paginación
- **Badges** de estado con colores semánticos

### Tipografía:
- **Font**: Inter (Google Fonts)
- **Pesos**: 300, 400, 500, 600, 700, 800

---

## 📊 Modelos de Datos Requeridos

```python
# Estadísticas se calculan desde estos modelos:
- HogarComunitario
  └── estado (aprobado, pendiente_visita, en_revision, rechazado)
  └── fecha_registro
  └── capacidad_maxima
  └── localidad

- MadreComunitaria (Agente Educativo)
  └── usuario (Usuario)

- Nino
  └── estado (activo, inactivo)
  └── fecha_ingreso
  └── hogar (ForeignKey)
  └── padre (ForeignKey)

- VisitaTecnica
  └── fecha_visita
  └── estado (programada, pendiente, realizada)
  └── hogar (ForeignKey)

- Solicitud (opcional)
  └── estado (pendiente, aprobada, rechazada)
```

---

## 🚀 Funcionalidades Implementadas

### ✅ Backend (views_dashboard.py)

1. **dashboard_admin()** - Vista principal
   - Calcula 9 estadísticas en tiempo real
   - Genera 4 gráficas (matriculas, estados, top hogares, solicitudes)
   - Lista 15 hogares más recientes
   - Anota cantidad de niños por hogar

2. **hogares_dashboard()** - Gestión de hogares
   - Filtros: localidad, estado, búsqueda
   - Agrupación por localidad
   - Conteo de niños activos por hogar

3. **hogar_detalle_api()** - API JSON
   - Información completa del hogar
   - Lista de niños con fotos
   - Documentos asociados
   - Visitas técnicas

4. **nino_detalle_api()** - API JSON
   - Datos del niño
   - Información del tutor
   - Documentos del niño

5. **preview_document()** - Previsualización
   - Detecta tipo de archivo (PDF/imagen)
   - Genera template con visor apropiado

6. **nino_carpeta_view()** - Carpeta completa
   - Renderiza vista con tabs
   - Información, tutor, documentos, historial

### ✅ Frontend (Templates HTML/CSS/JS)

1. **dashboard_admin.html**
   - 6 tarjetas de estadísticas
   - 4 gráficas con Chart.js
   - Tabla de hogares recientes
   - Modal de detalles de hogar
   - Búsqueda global

2. **hogares_dashboard.html**
   - Barra de filtros
   - Toggle de vistas (localidad/grilla)
   - Tarjetas de hogares por localidad
   - Modal con vista detallada
   - Vista de niños tipo carpetas

3. **nino_carpeta.html**
   - Header con foto y datos principales
   - 4 tabs organizados
   - Timeline de historial
   - Tarjeta del tutor
   - Grid de documentos
   - Botones de acción (editar, imprimir, exportar)

4. **preview_document.html**
   - Visor PDF con iframe
   - Visor de imágenes con zoom
   - Controles de zoom y rotación
   - Atajos de teclado
   - Botón de descarga

---

## 🔧 Configuración e Instalación

### 1. Archivos Creados/Modificados:

```bash
# Nuevos archivos
core/views_dashboard.py
templates/admin/dashboard_admin.html
templates/admin/nino_carpeta.html
templates/admin/preview_document.html

# Archivos modificados
core/views.py (import agregado)
icbfconecta/urls.py (5 URLs agregadas)
```

### 2. Dependencias:

```html
<!-- Ya incluidas en el proyecto -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
```

### 3. Migraciones:

No requiere migraciones adicionales. Usa los modelos existentes.

---

## 📱 Responsive Design

### Breakpoints:
- **Desktop**: > 1024px - Sidebar fija, dos columnas
- **Tablet**: 768px - 1024px - Sidebar colapsable, columna única
- **Mobile**: < 768px - Menú hamburguesa, tarjetas apiladas

### Adaptaciones:
```css
@media (max-width: 1024px) {
  .sidebar { transform: translateX(-100%); }
  .main-content { margin-left: 0; }
  .charts-grid { grid-template-columns: 1fr; }
  .hogar-detalle-grid { grid-template-columns: 1fr; }
}
```

---

## 🎯 Flujo de Navegación

```
Dashboard Admin (/)
├── Ver Estadísticas Generales
├── Analizar Gráficas
├── Click en "Gestión de Hogares"
│   ├── Filtrar por Localidad/Estado
│   ├── Click en Tarjeta de Hogar
│   │   └── Modal Detalle de Hogar
│   │       ├── Información General
│   │       ├── Click en Niño (Carpeta)
│   │       │   └── Vista Carpeta del Niño
│   │       │       ├── Tab Información
│   │       │       ├── Tab Tutor
│   │       │       ├── Tab Documentos
│   │       │       │   └── Click en Documento
│   │       │       │       └── Preview Integrado (PDF/Imagen)
│   │       │       └── Tab Historial
│   │       └── Ver Documentos del Hogar
│   │           └── Preview Documento
└── Exportar Reportes (CSV/PDF)
```

---

## 🧪 Ejemplos de Uso

### 1. Ver Dashboard
```
URL: /dashboard/admin/
Vista: Estadísticas + Gráficas + Tabla
```

### 2. Gestionar Hogares
```
URL: /dashboard/admin/hogares/?localidad=Usaquén&estado=aprobado
Vista: Hogares filtrados por localidad
```

### 3. Ver Detalles de Hogar (AJAX)
```
URL: /api/hogares/5/detalle/
Response: JSON con niños, visitas, documentos
```

### 4. Ver Carpeta de Niño
```
URL: /ninos/12/carpeta/
Vista: Información completa + tabs
```

### 5. Previsualizar Documento
```
URL: /preview/nino/12/registro_civil/
Vista: Visor PDF o imagen con zoom
```

---

## 🔒 Seguridad

- **@login_required**: Todas las vistas requieren autenticación
- **get_object_or_404**: Validación de objetos
- **Validación de permisos**: Por rol de usuario
- **URLs parametrizadas**: Sin inyección SQL
- **XSS Protection**: Django templates auto-escape

---

## 🎓 Mejoras Futuras

### Corto Plazo:
- [ ] Exportar datos a Excel/CSV desde el dashboard
- [ ] Filtro por rango de fechas en gráficas
- [ ] Vista de mapa con geolocalización de hogares
- [ ] Notificaciones en tiempo real (WebSockets)

### Mediano Plazo:
- [ ] Dashboard de comparativas entre regionales
- [ ] Alertas automáticas de visitas vencidas
- [ ] Generación automática de reportes PDF
- [ ] Integración con Google Maps

### Largo Plazo:
- [ ] Dashboard predictivo con IA
- [ ] Análisis de tendencias con ML
- [ ] App móvil con React Native
- [ ] Sistema de firma digital para actas

---

## 📞 Soporte Técnico

**Desarrollado para**: ICBF Conecta  
**Versión**: 1.0.0  
**Fecha**: Diciembre 2025  
**Framework**: Django 5.2  
**Frontend**: Vanilla JS + Chart.js  

---

## 📝 Changelog

### v1.0.0 (2025-12-10)
- ✨ Dashboard administrativo completo
- 📊 4 gráficas interactivas con Chart.js
- 🏠 Vista de hogares por localidad
- 👶 Sistema de carpetas de niños
- 📄 Previsualización de documentos PDF/imágenes
- 🔍 Búsqueda y filtros avanzados
- 📱 Diseño responsive
- 🎨 UI moderna con Inter font
- ⚡ APIs JSON para modales
- 🔐 Sistema de seguridad integrado

---

## 🙏 Agradecimientos

Este dashboard fue diseñado pensando en la mejor experiencia de usuario para los administradores del ICBF, facilitando la gestión integral de hogares comunitarios y proporcionando visibilidad completa sobre el estado del programa.

**¡Gracias por usar ICBF Conecta!** 🎉
