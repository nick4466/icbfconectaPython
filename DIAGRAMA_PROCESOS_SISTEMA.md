# Diagrama de Procesos - Sistema ICBF Conecta

## 1. Arquitectura General del Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SISTEMA ICBF CONECTA                            │
│                      (Plataforma Django 5.2)                            │
└─────────────────────────────────────────────────────────────────────────┘

                            ┌──────────────────┐
                            │   USUARIO LOGIN  │
                            └────────┬─────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
        ┌────────▼─────────┐  ┌─────▼──────────┐  ┌────▼──────────┐
        │  ADMINISTRADOR   │  │ MADRE          │  │ PADRE         │
        │  - Gestión User  │  │ COMUNITARIA    │  │ - Consultar   │
        │  - Configuración │  │ - Planeación   │  │   desarrollo  │
        │  - Reportes      │  │ - Evaluaciones │  │ - Novedades   │
        │  - Auditoría     │  │ - Documentación│  │ - Firmas      │
        └──────────────────┘  └────────────────┘  └───────────────┘
```

---

## 2. Flujo de Autenticación y Roles

```
┌─────────────────┐
│  PÁGINA LOGIN   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ VALIDAR CREDENCIALES        │
│ (core/backends.py)          │
└────────┬────────────────────┘
         │
    ┌────┴────┐
    │          │
    ▼          ▼
┌─────────┐ ┌──────────┐
│ VÁLIDO  │ │ INVÁLIDO │
└────┬────┘ └────┬─────┘
     │           │
     ▼           ▼
┌──────────┐  ┌──────────────┐
│ ASIGNAR  │  │ MOSTRAR      │
│ ROL      │  │ ERROR        │
│ @rol_    │  │ VOLVER LOGIN │
│ requerido│  └──────────────┘
└────┬─────┘
     │
     ▼
┌──────────────────────────┐
│ CARGAR DASHBOARD         │
│ SEGÚN ROL DEL USUARIO    │
└──────────────────────────┘
```

---

## 3. Proceso de Carga Dinámica de Ubicaciones (Cascada)

```
┌────────────────────────────────────────────────────────────┐
│      FORMULARIO CON UBICACIÓN (Crear Usuario/Hogar)       │
└────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐
    │ SELECCIONAR         │
    │ DEPARTAMENTO        │
    └────────┬────────────┘
             │
             ▼
    ┌─────────────────────┐         ┌──────────────────────┐
    │ DISPARAR AJAX       │────────▶│ core/views.py        │
    │ fetch /api/         │         │ obtener_municipios   │
    │ municipios?dep=XX   │         └──────────┬───────────┘
    └─────────────────────┘                    │
             ▲                                  ▼
             │                    ┌──────────────────────┐
             │                    │ QUERY Q() MUNICIPIOS │
             │                    │ filter(departamento) │
             │                    └──────────┬───────────┘
             │                               │
             │                               ▼
             │                    ┌──────────────────────┐
             └────────────────────│ DEVOLVER JSON        │
                                  │ LLENAR SELECT        │
                                  └──────────────────────┘

    Repeat: Municipio → Localidad → Barrio (Bogotá)
```

---

## 4. Flujo Principal: Gestión de Hogares y Madres

```
┌──────────────────────────────────────────────────────────────┐
│              PROCESO: CREAR NUEVO HOGAR                      │
└──────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 1. ADMINISTRADOR ACCEDE A CREAR HOGAR   │
│    (Validar @rol_requerido)             │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 2. LLENAR FORMULARIO                    │
│    - Nombre hogar                       │
│    - Ubicación (cascada)                │
│    - Datos contacto                     │
│    - Upload documentos (FileSizeVal)    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│ 3. VALIDAR DATOS                        │
│    - Campos requeridos                  │
│    - Tamaño archivos (<5MB)             │
│    - Ubicación válida                   │
└────────────┬────────────────────────────┘
             │
        ┌────┴────┐
        │          │
        ▼          ▼
    ┌─────┐    ┌────────┐
    │VÁLIDO   │  INVÁLIDO
    └────┬─────┘  └──┬─────┐
         │           │     │
         ▼           ▼     │
    ┌────────┐   ┌─────────────────┐
    │GUARDAR │   │ MOSTRAR         │
    │EN BD   │   │ ERRORES EN FORM │
    └────┬───┘   └─────────────────┘
         │
         ▼
    ┌─────────────────────┐
    │ CREAR CARPETA MEDIA │
    │ /media/hogares/XX/  │
    └────────┬────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │ GUARDAR DOCUMENTOS EN CARPETA       │
    │ /media/hogares/{id}/                │
    └────────┬────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ CREAR REGISTRO EN BD (Hogar model)   │
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ REGISTRAR EVENTO EN AUDITORÍA        │
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ ENVIAR NOTIFICACIÓN A USUARIOS       │
    │ (notifications app)                  │
    └──────────────────────────────────────┘
```

---

## 5. Flujo: Inscripción de Madre Comunitaria

```
┌─────────────────────────────────────────────────────┐
│   PROCESO: INSCRIPCIÓN MADRE COMUNITARIA            │
└──────────────────────────────┬──────────────────────┘
                               │
        ┌──────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────┐
│ 1. SELECCIONAR HOGAR COMUNITARIO (Padre/Admin)  │
└──────────┬───────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────┐
│ 2. CREAR SOLICITUD DE MATRICULACIÓN             │
│    (Modelo: SolicitudMatriculacion)             │
│    - Fecha solicitud                            │
│    - Datos madre comunitaria                    │
│    - Documentos antecedentes                    │
│    - Estado: PENDIENTE                          │
└──────────┬───────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────┐
│ 3. VALIDACIONES                                  │
│    - Documentos completos                       │
│    - Antecedentes válidos                       │
│    - Capacidad hogar vs cupos                   │
└──────────┬───────────────────────────────────────┘
           │
      ┌────┴────┐
      │          │
      ▼          ▼
  ┌─────┐    ┌──────────┐
  │PASA │    │NO PASA   │
  └──┬──┘    └────┬─────┘
     │            │
     ▼            ▼
┌──────────┐  ┌────────────────┐
│APROBAR   │  │RECHAZAR + ENVIAR│
│SOLICITUD │  │EMAIL NOTIFICAC. │
└────┬─────┘  └────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ 4. CREAR USUARIO (core.Usuario)      │
│    - Email                           │
│    - Contraseña temporal             │
│    - Rol: madre_comunitaria          │
│    - Link al Hogar (FK)              │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ 5. GENERAR CARPETA MEDIA             │
│    /media/madres_documentos/{doc}/   │
│    - antecedentes/                   │
│    - cedulas/                        │
│    - educacion/                      │
│    - firmas/                         │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ 6. ENVIAR EMAIL                      │
│    - Notificar aprobación            │
│    - Credenciales temporales         │
│    - Link cambiar contraseña         │
│    (EmailLog registra envío)         │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ 7. CREAR NOTIFICACIÓN EN SISTEMA     │
│    (notifications app)               │
└──────────────────────────────────────┘
```

---

## 6. Flujo: Planeación Educativa y Documentación

```
┌──────────────────────────────────────────────────────┐
│   PROCESO: CREAR PLANEACIÓN SEMANAL/MENSUAL         │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ MADRE COMUNITARIA ACCEDE   │
        │ A CREAR PLANEACIÓN         │
        │ (planeaciones app)         │
        └────────┬───────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────┐
        │ SELECCIONAR:                       │
        │ - Período (semana/mes)             │
        │ - Dimensiones a trabajar           │
        │ - Objetivo educativo               │
        │ - Materiales disponibles           │
        └────────┬─────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────┐
        │ CREAR DOCUMENTACIÓN POR DIMENSIÓN │
        │ (modelo: Documentacion)            │
        │ - Descripción actividades          │
        │ - Indicadores de logro             │
        │ - Archivos adjuntos (fotos/videos) │
        └────────┬─────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────┐
        │ GUARDAR DOCUMENTOS                 │
        │ /media/planeaciones/{id}/          │
        │ /media/documentacion/{id}/         │
        └────────┬─────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────┐
        │ ESTADO: PLANEACIÓN ACTIVA          │
        └────────┬─────────────────────────────┘
                 │
        ┌────────┴──────────┐
        │                   │
        ▼                   ▼
    ┌──────────┐       ┌─────────────┐
    │DURANTE   │       │AL FINALIZAR │
    │PERÍODO   │       │PERÍODO      │
    └────┬─────┘       └──────┬──────┘
         │                    │
         ▼                    ▼
    ┌─────────────┐    ┌─────────────────────┐
    │REGISTRAR    │    │GENERAR REPORTE PDF  │
    │SEGUIMIENTO  │    │(xhtml2pdf)          │
    │DIARIO       │    │- Actividades        │
    │(desarrollo  │    │- Logros niños       │
    │app)         │    │- Fotos documentadas │
    └─────────────┘    └─────────────────────┘
```

---

## 7. Flujo: Seguimiento del Desarrollo Infantil

```
┌─────────────────────────────────────────────────┐
│ PROCESO: EVALUACIÓN MULTIDIMENSIONAL DEL NIÑO   │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ MADRE COMUNITARIA REGISTRA NIÑO  │
    │ (core app)                       │
    │ - Datos personales               │
    │ - Foto                           │
    │ - Fecha nacimiento               │
    │ - Relación con familia           │
    └──────┬───────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │ CREAR CARPETA MEDIA              │
    │ /media/ninos/{id}/               │
    │ - fotos/                         │
    │ - documentos/                    │
    └──────┬───────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │ CREAR SEGUIMIENTO DIARIO         │
    │ (modelo: DesarrolloNino)         │
    │ Registrar:                       │
    │ - Observaciones conducta         │
    │ - Alimentación                   │
    │ - Sueño                          │
    │ - Desarrollo motor               │
    └──────┬───────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │ REALIZAR EVALUACIÓN DIMENSIONAL  │
    │ (modelo: EvaluacionDimension)    │
    │                                  │
    │ Por cada dimensión:              │
    │ ├─ Cognitiva                     │
    │ ├─ Comunicativa                  │
    │ ├─ Socioemocional                │
    │ ├─ Física                        │
    │ └─ Creativa                      │
    │                                  │
    │ Asignar: Rango de logro          │
    │ - Inicial                        │
    │ - En progreso                    │
    │ - Alcanzado                      │
    └──────┬───────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │ GUARDAR EN BD                    │
    │ (No sobrescribir - historial)    │
    └──────┬───────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │ GENERAR REPORTE DE DESARROLLO    │
    │ - Gráficos por dimensión         │
    │ - Evolución temporal             │
    │ - Recomendaciones                │
    │ - PDF descargable                │
    └──────────────────────────────────┘
```

---

## 8. Flujo: Sistema de Notificaciones y Emails

```
┌───────────────────────────────────────────────────┐
│ PROCESO: ENVÍO DE NOTIFICACIONES Y EMAILS         │
└─────────────────────┬─────────────────────────────┘
                      │
        ┌─────────────┼──────────────┐
        │             │              │
        ▼             ▼              ▼
    ┌────────┐  ┌──────────┐  ┌──────────┐
    │EVENTO  │  │TAREA     │  │SOLICITUD │
    │DEL SIS │  │PROGRAMADA│  │USUARIO   │
    └───┬────┘  └────┬─────┘  └────┬─────┘
        │            │             │
        ▼            ▼             ▼
    ┌──────────────────────────────────────┐
    │ DISPARAR TRIGGER EN SIGNALS          │
    │ (post_save, post_delete)             │
    │ (APScheduler para tareas)            │
    │ (core/scheduler.py)                  │
    └──────┬───────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │ CREAR REGISTRO NOTIFICACIÓN          │
    │ (notifications.Notification)         │
    │ - Usuario destinatario               │
    │ - Tipo de evento                     │
    │ - Mensaje                            │
    │ - Leído: False                       │
    └──────┬───────────────────────────────┘
           │
      ┌────┴────────────┐
      │                 │
      ▼                 ▼
  ┌─────────────┐  ┌───────────────┐
  │¿ENVIAR      │  │¿TAREA EMAIL?  │
  │EMAIL?       │  └────┬──────────┘
  │(settings)   │       │
  └────┬────────┘       ▼
       │         ┌──────────────────┐
       ▼         │ ENVIAR EMAIL     │
   ┌──────────────────────────────┐  │
   │ OBTENER TEMPLATE EMAIL       │  │
   │ /templates/emails/{tipo}.html│  │
   └───┬───────────────────────────┘  │
       │                               │
       ▼                               ▼
   ┌──────────────────────────────┐  ┌─────────────────┐
   │ GENERAR CONTENIDO HTML       │  │ RENDERIZAR      │
   │ (insertar variables)         │  │ TEMPLATE        │
   └───┬───────────────────────────┘  └────┬────────────┘
       │                                    │
       ▼                                    ▼
   ┌──────────────────────────────┐  ┌──────────────────┐
   │ ENVIAR VÍA SMTP              │  │ CREAR EMAILLOG   │
   │ (django.core.mail)           │  │ - Asunto         │
   │ - Credenciales .env          │  │ - Destinatario   │
   │                              │  │ - Fecha envío    │
   └──────────────────────────────┘  │ - Estado         │
                                      └──────────────────┘
```

---

## 9. Flujo: Generación de Reportes en PDF

```
┌──────────────────────────────────────────┐
│ PROCESO: GENERAR REPORTE PDF             │
└────────────────┬─────────────────────────┘
                 │
        ┌────────┴───────────┐
        │                    │
        ▼                    ▼
    ┌──────────┐        ┌──────────────┐
    │DESARROLLO│        │ASISTENCIA    │
    │INFANTIL  │        │MENSUAL       │
    └────┬─────┘        └────┬─────────┘
         │                   │
         ▼                   ▼
    ┌────────────────────────────────────┐
    │ OBTENER DATOS DE BD                │
    │ - QuerySet filtrado                │
    │ - Contexto datos usuario           │
    │ - Gráficos/estadísticas            │
    └──────┬───────────────────────────────┘
           │
           ▼
    ┌────────────────────────────────────┐
    │ CARGAR TEMPLATE HTML               │
    │ /templates/reporte/{tipo}.html     │
    │ - CSS INLINE OBLIGATORIO           │
    │ - Estructura tabla/gráficos        │
    └──────┬───────────────────────────────┘
           │
           ▼
    ┌────────────────────────────────────┐
    │ RENDERIZAR TEMPLATE                │
    │ (render_to_string)                 │
    │ - Insertar datos en variables      │
    │ - Compilar HTML final              │
    └──────┬───────────────────────────────┘
           │
           ▼
    ┌────────────────────────────────────┐
    │ CONVERTIR HTML A PDF               │
    │ (xhtml2pdf.pisa)                   │
    │ - Validar HTML válido              │
    │ - Aplicar estilos CSS              │
    │ - Generar buffer bytes             │
    └──────┬───────────────────────────────┘
           │
           ▼
    ┌────────────────────────────────────┐
    │ GUARDAR O DESCARGAR                │
    │                                    │
    │ OPCIÓN 1: Descargar directo        │
    │ HttpResponse(buffer,               │
    │  content_type='application/pdf')   │
    │                                    │
    │ OPCIÓN 2: Guardar en media         │
    │ /media/reportes/{id}/              │
    │ + Registrar en modelo Reporte      │
    └────────────────────────────────────┘
```

---

## 10. Flujo: Gestión de Solicitudes (Matriculación/Retiro)

```
┌────────────────────────────────────────────┐
│ PROCESO: GESTIÓN SOLICITUD MATRICULACIÓN   │
└─────────────────┬──────────────────────────┘
                  │
                  ▼
    ┌──────────────────────────────────┐
    │ PADRE/ADMIN CREA SOLICITUD       │
    │ SolicitudMatriculacion           │
    │ - Fecha solicitud                │
    │ - Hogar destino                  │
    │ - Documentos requeridos          │
    │ - Estado: PENDIENTE              │
    └──────┬───────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │ GUARDAR EN /media/solicitudes/   │
    │ {id}/                            │
    └──────┬───────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │ CREAR NOTIFICACIÓN               │
    │ → Madre comunitaria              │
    │ → Administrador                  │
    └──────┬───────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │ ENVIAR EMAIL NOTIFICACIÓN        │
    │ (correos app)                    │
    │ Registrar en EmailLog            │
    └──────┬───────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │ MADRE/ADMIN REVISA               │
    │ - Valida documentos              │
    │ - Verifica capacidad cupos       │
    │ - Decide APROBAR/RECHAZAR        │
    └──────┬───────────────────────────┘
           │
      ┌────┴──────┐
      │            │
      ▼            ▼
  ┌─────────┐  ┌────────┐
  │APROBAR  │  │RECHAZAR│
  └────┬────┘  └───┬────┘
       │           │
       ▼           ▼
   ┌────────┐  ┌──────────────┐
   │CAMBIAR │  │CAMBIAR ESTADO│
   │ESTADO A│  │A RECHAZADA   │
   │APROBADA│  │ENVIAR EMAIL  │
   │        │  │NOTIFICACIÓN  │
   │ASIGNAR │  │              │
   │CUPO    │  └──────────────┘
   │CREAR   │
   │USUARIO │
   │(si no  │
   │existe) │
   └────────┘

Similar para: SOLICITUD RETIRO
```

---

## 11. Arquitectura de Capas del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                  CAPA PRESENTACIÓN                          │
│  Templates HTML + Bootstrap + JavaScript (AJAX)            │
│  - Dashboard Madre / Padre / Admin                         │
│  - Formularios dinámicos (cascadas)                        │
│  - Vistas reportes                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  CAPA LÓGICA (Views)                        │
│  - core/views.py (7515 líneas - lógica central)           │
│  - core/views_dashboard.py (dashboards)                   │
│  - {app}/views.py (lógica específica)                     │
│  - Decoradores: @rol_requerido, @login_required           │
│  - AJAX endpoints para cascadas                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  CAPA SERVICIOS                             │
│  - {app}/services.py (lógica de negocios)                 │
│  - Generación PDF (xhtml2pdf)                             │
│  - Email (correos/models.py)                              │
│  - APScheduler (core/scheduler.py)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  CAPA DE DATOS                              │
│  - ORM Django: Models                                       │
│  - {app}/models.py                                         │
│  - Relaciones: FK, M2M                                     │
│  - Signals: pre_save, post_save (core/signals.py)         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              BASES DE DATOS + ALMACENAMIENTO               │
│  - SQLite (desarrollo)                                      │
│  - /media: Archivos documentos, PDFs, imágenes            │
│  - Estructura: madres_documentos/{cedula}/                │
│               hogares/{id}/                                 │
│               ninos/{id}/                                   │
│               reportes/                                     │
│               solicitudes/                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 12. Flujo de Validación de Archivos (Uploads)

```
┌────────────────────────────────────┐
│ USUARIO SUBE ARCHIVO (form.py)     │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ INICIALIZAR FileSizeValidationMixin│
│ - MAX_UPLOAD_SIZE_BYTES = 5 MB     │
│ - FILE_FIELDS = ['campo1','campo2']│
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ EJECUTAR clean() del formulario    │
└─────────────┬──────────────────────┘
              │
              ▼
┌────────────────────────────────────┐
│ PARA CADA ARCHIVO ENVIADO:         │
│                                    │
│ 1. Obtener tamaño en bytes         │
│ 2. Comparar: size > MAX_SIZE?      │
│ 3. Obtener extensión               │
│ 4. Validar extensión permitida     │
└─────────────┬──────────────────────┘
              │
        ┌─────┴───────┐
        │             │
        ▼             ▼
    ┌───────┐     ┌──────────┐
    │VÁLIDO │     │INVÁLIDO  │
    └───┬───┘     └────┬─────┐
        │              │     │
        ▼              ▼     │
    ┌─────────┐   ┌──────────────────┐
    │CONTINUAR│   │AGREGAR ERROR AL  │
    │VALIDAR  │   │FORMULARIO        │
    │OTROS    │   │ValidationError() │
    │CAMPOS   │   └──────────────────┘
    └────┬────┘
         │
    ┌────┴──────────┐
    │               │
    ▼               ▼
┌─────────┐    ┌─────────────┐
│VÁLIDO   │    │INVÁLIDO     │
└────┬────┘    └──────┬──────┘
     │                │
     ▼                ▼
 ┌─────────────────────────────┐
 │ GUARDAR ARCHIVO EN:         │
 │ /media/{app}/{ruta}/        │
 │ Usar: madre_upload_path()   │
 │       hogar_upload_path()   │
 │       nino_upload_path()    │
 │                             │
 │ Nombre: {cedula}_{fecha}    │
 └─────────────────────────────┘
```

---

## 13. Ciclo de Vida de un Registro (Ejemplo: Usuario)

```
┌──────────────────────────────────────────────────┐
│ 1. CREAR USUARIO (SolicitudMatriculacion aprobada)│
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│ 2. SIGNAL: pre_save (core/signals.py)             │
│    - Validaciones antes de guardar                │
│    - Transformar datos si es necesario            │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│ 3. GUARDAR EN BD (Usuario.objects.create())       │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│ 4. SIGNAL: post_save (core/signals.py)            │
│    - Crear carpeta media                         │
│    - Crear notificaciones                        │
│    - Enviar email                                │
│    - Registrar en auditoría                      │
└────────────────┬─────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│ 5. USUARIO ACTIVO EN SISTEMA                      │
│    - Puede loguearse                              │
│    - Acceso según rol (@rol_requerido)           │
└────────────────┬─────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    ┌────────┐        ┌─────────┐
    │ACTIVO  │        │INACTIVO │
    │        │        │(admin)  │
    └───┬────┘        └────┬────┘
        │                  │
        ▼                  ▼
    ┌──────────┐    ┌───────────────┐
    │USAR      │    │NO ACCESO A    │
    │SISTEMA   │    │VISTAS (403)   │
    │          │    │               │
    │          │    │Pero:          │
    │          │    │- Conservar    │
    │          │    │  datos        │
    │          │    │- Auditoría    │
    └──────────┘    └───────────────┘
```

---

## 14. Estructura General de Aplicaciones Django

```
icbfconecta/
├── APLICACIONES PRINCIPALES
│
├── core/                    ← NÚCLEO DEL SISTEMA
│   ├── models.py           (Usuario, Hogar, Nino, Departamento, etc)
│   ├── views.py            (7515 líneas - lógica central)
│   ├── views_dashboard.py  (dashboards por rol)
│   ├── forms.py            (formularios con cascadas AJAX)
│   ├── decorators.py       (@rol_requerido)
│   ├── backends.py         (autenticación custom)
│   ├── signals.py          (post_save, pre_delete)
│   ├── scheduler.py        (APScheduler - tareas programadas)
│   ├── static/             (CSS, JS)
│   ├── migrations/         (historial de cambios BD)
│   └── tests.py            (test_barrios.py, etc)
│
├── planeaciones/           ← PLANIFICACIÓN EDUCATIVA
│   ├── models.py           (Planeacion, Documentacion, Dimension)
│   ├── views.py
│   ├── forms.py
│   └── signals.py          (crear documentación)
│
├── desarrollo/             ← DESARROLLO INFANTIL
│   ├── models.py           (EvaluacionDimension, DesarrolloNino)
│   ├── views.py
│   ├── services.py         (generación reportes PDF)
│   └── tests.py
│
├── novedades/              ← EVENTOS/INCIDENTES
│   ├── models.py           (Novedad)
│   ├── views.py
│   ├── signals.py
│   └── forms.py
│
├── correos/                ← COMUNICACIÓN EMAIL
│   ├── models.py           (EmailLog)
│   ├── views.py            (gestión emails)
│   └── forms.py
│
├── asistencia/             ← CONTROL DE ASISTENCIA
│   ├── models.py
│   ├── views.py
│   └── forms.py
│
├── notifications/          ← SISTEMA DE ALERTAS
│   ├── models.py           (Notification)
│   ├── views.py
│   └── urls.py
│
├── icbfconecta/            ← CONFIGURACIÓN PROYECTO
│   ├── settings.py         (INSTALLED_APPS, BD, EMAIL)
│   ├── urls.py             (rutas principales)
│   ├── wsgi.py
│   └── context_processors.py
│
├── templates/              ← HTML TEMPLATES
│   ├── base.html
│   ├── login.html
│   ├── home.html
│   ├── madre/
│   ├── padre/
│   ├── admin/
│   ├── emails/             (plantillas email)
│   ├── reporte/            (templates PDF)
│   └── ...
│
├── static/                 ← ASSETS (CSS, JS)
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/                  ← ARCHIVOS CARGADOS (DINÁMICO)
│   ├── madres_documentos/  {cedula}/
│   ├── hogares/            {id}/
│   ├── ninos/              {id}/
│   ├── reportes/           {id}/
│   ├── planeaciones/       {id}/
│   ├── documentacion/      {id}/
│   ├── solicitudes/        {id}/
│   └── correos_adjuntos/   {id}/
│
└── db.sqlite3              ← BASE DATOS (desarrollo)
```

---

## 15. Resumen de Flujos Críticos

```
┌─────────────────────────────────────────────────────────────┐
│              FLUJOS CRÍTICOS DEL SISTEMA                    │
└─────────────────────────────────────────────────────────────┘

ENTRADA AL SISTEMA:
  Login → @rol_requerido → Dashboard específico → Menú por rol

GESTIÓN USUARIOS:
  Solicitud → Validación → Crear Usuario → Enviar email
              → Notificación → Carpeta media

EDUCACIÓN:
  Planeación → Documentación por Dimensión → Registrar evaluaciones
  → Generar PDF → Descarga/Archivo

DESARROLLO:
  Seguimiento diario → Evaluación dimensional (multi-registro)
  → Gráficos evolución → Reporte PDF → Padre consulta

ALERTAS:
  Evento → Signal post_save → Crear Notificación
  → Enviar email (si habilitado) → Usuario recibe

ARCHIVOS:
  Upload → FileSizeValidation → Guardar en /media/{app}/{ruta}
  → Registrar en modelo → Disponible en vistas
```

---

## 16. Integraciones Externas

```
┌──────────────────────────────────────────┐
│       INTEGRACIONES DEL SISTEMA          │
└──────────────────────────────────────────┘

EMAIL (SMTP)
  - Credenciales en .env
  - django.core.mail.EmailMessage
  - Plantillas en templates/emails/
  - Registro en EmailLog model
  
GENERACIÓN PDF
  - Librería: xhtml2pdf==0.2.17
  - Entrada: HTML template
  - Salida: Buffer bytes → HttpResponse o /media/
  
ALMACENAMIENTO ARCHIVOS
  - Sistema de archivos local (/media/)
  - Rutas dinámicas por documento/id
  - Validación tamaño en formularios
  
AUTENTICACIÓN
  - Django auth personalizada
  - AbstractUser → Usuario custom
  - Roles en modelo Rol (3 tipos)
  
TAREAS PROGRAMADAS
  - APScheduler 3.10.4
  - Configurado en core/scheduler.py
  - Ejemplo: enviar recordatorios
  
PROCESAMIENTO IMÁGENES
  - Pillow 12.0.0
  - Redimensionamiento automático
  
EXPORTACIÓN DATOS
  - openpyxl → Excel
  - CSV generado en vistas
```

---

## 17. Puntos de Decisión y Validaciones

```
┌──────────────────────────────────────────────────────────┐
│      PUNTOS DE DECISIÓN EN FLUJOS                       │
└──────────────────────────────────────────────────────────┘

AUTENTICACIÓN
  ├─ ¿Usuario existe? → Sí/No → Login/Error
  ├─ ¿Rol activo? → Sí/No → Acceso/403
  └─ ¿Token válido? → Sí/No → Reset/Error

CARGA DE ARCHIVOS
  ├─ ¿Tamaño < 5MB? → Sí/No → Guardar/Error
  ├─ ¿Extensión válida? → Sí/No → Guardar/Error
  └─ ¿Carpeta existe? → Sí/No → Crear/Error

PLANEACIÓN
  ├─ ¿Madre tiene hogar? → Sí/No → Crear/Error
  ├─ ¿Periodo duplicado? → Sí/No → Sobrescribir/Error
  └─ ¿Documentación completa? → Sí/No → Activar/Error

SOLICITUDES
  ├─ ¿Documentos completos? → Sí/No → Revisar/Error
  ├─ ¿Hogar tiene cupo? → Sí/No → Aprobar/Espera
  └─ ¿Antecedentes válidos? → Sí/No → Aprobar/Rechazar

NOTIFICACIONES
  ├─ ¿Email habilitado? → Sí/No → Enviar/Solo BD
  ├─ ¿Dirección válida? → Sí/No → Enviar/Fallo
  └─ ¿Registrar log? → Siempre → EmailLog
```

---

## 18. Diagrama de Interacción Usuario-Sistema

```
┌────────────────────────────────────────────────────────┐
│     INTERACCIÓN: USUARIO ←→ SISTEMA ICBF CONECTA      │
└────────────────────────────────────────────────────────┘

USUARIO (MADRE COMUNITARIA)

1. ACCEDE A PÁGINA LOGIN
         ↓
2. INGRESA CREDENCIALES
         ↓
3. [SISTEMA] Valida contra BD, verifica rol
         ↓
4. [SISTEMA] Carga template dashboard madre
         ↓
5. VISUALIZA OPCIONES:
   - Ver niños a cargo
   - Crear planeación
   - Registrar evaluaciones
   - Ver solicitudes
   - Consultar reportes
         ↓
6. SELECCIONA: "Crear Planeación"
         ↓
7. [SISTEMA] Carga formulario con cascadas (Departamento, etc)
         ↓
8. COMPLETA FORMULARIO + CARGA ARCHIVOS
         ↓
9. [SISTEMA] FileSizeValidation + validar campos
         ↓
10. ENVÍA FORMULARIO
         ↓
11. [SISTEMA] post_save signal:
    - Guardar documentos en /media/
    - Crear notificación
    - Enviar email a admin
         ↓
12. [SISTEMA] Mostrar confirmación + PDF preview
         ↓
13. USUARIO VE: "Planeación creada exitosamente"
```

---

## 19. Flujo de Errores y Recuperación

```
┌──────────────────────────────────────────┐
│    MANEJO DE ERRORES EN EL SISTEMA       │
└──────────────────────────────────────────┘

ERROR: Archivo > 5MB
└─ clean() → ValidationError
   └─ Template muestra: "Archivo demasiado grande"
   └─ Permitir reintentar

ERROR: Ubicación no encontrada
└─ Cascada AJAX retorna JSON vacío
   └─ JavaScript: deshabilitar select siguiente
   └─ Usuario ve: "Seleccionar primero municipio"

ERROR: Usuario sin permisos
└─ @rol_requerido verifica rol
   └─ raise PermissionDenied
   └─ Redireccionar a 403.html

ERROR: Base de datos no disponible
└─ DatabaseError capturado
   └─ Registrar en logs
   └─ Mostrar: "Servicio temporalmente no disponible"

ERROR: Email no envía
└─ try/except en correos/models.py
   └─ Registrar intento en EmailLog (status=FAILED)
   └─ Mostrar al admin en panel de emails
   └─ Reintentar manualmente

ERROR: PDF no genera
└─ xhtml2pdf.pisa retorna errores
   └─ Validar HTML está correcto
   └─ Mostrar error y permitir descargar como HTML

REGISTROS DE ERROR
└─ Django logs: /logs/django.log
└─ EmailLog model: historial envíos
└─ Notificaciones fallidas: notifications table
```

---

## Conclusión

Este diagrama de procesos representa el **flujo integral** del sistema ICBF Conecta, desde la autenticación del usuario hasta la generación de reportes y comunicaciones. Cada proceso está diseñado para:

- ✅ **Validar datos** en múltiples capas
- ✅ **Mantener integridad** de información
- ✅ **Documentar eventos** en auditoría
- ✅ **Comunicar cambios** a usuarios relevantes
- ✅ **Generar reportes** para seguimiento
- ✅ **Facilitar recuperación** ante errores

