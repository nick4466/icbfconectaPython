# PROMPT MAESTRO: Mapa de Procesos General - Sistema ICBF Conecta

**Objetivo:** Generar un **diagrama maestro BPMN 2.0** que represente **TODOS los procesos principales del sistema ICBF Conecta** interconectados, mostrando el flujo integral de la plataforma.

**Nivel:** Macro (Vista de procesos de negocio, NO detalle técnico)  
**Estándar:** BPMN 2.0 / ISO/IEC 19510  
**Alcance:** Sistema completo - Entrada de usuarios → Ciclo de vida completo en la plataforma

---

## 🎯 CONTEXTO DEL SISTEMA ICBF CONECTA

**Propósito:** Plataforma Django 5.2 para gestión integral de programas de atención a madres comunitarias e hijos en el ICBF (Instituto Colombiano de Bienestar Familiar).

**Actores Principales del Sistema:**
1. **Padre/Madre de familia** - Solicita matriculación, consulta desarrollo
2. **Madre Comunitaria** - Gestiona niños, planifica, documenta, evalúa
3. **Administrador ICBF** - Gestiona usuarios, supervisa, aprueba solicitudes
4. **Sistema** - Procesa datos, valida, almacena, notifica
5. **Servicios Externos** - Email (SMTP), Almacenamiento (Filesystem)

---

## ✅ LO QUE DEBE INCLUIR EL DIAGRAMA MAESTRO

### 1. PROCESOS PRINCIPALES IDENTIFICADOS

El diagrama **DEBE mostrar explícitamente ESTOS 9 procesos:**

#### **PROCESOS NÚCLEO (De mayor criticidad):**

```
1. INGRESO AL SISTEMA
   Entrada: Usuario no autenticado
   Proceso: Login → Validación → Asignación de rol → Acceso a dashboard
   Salida: Usuario autenticado en su rol específico

2. GESTIÓN DE USUARIOS MADRE COMUNITARIA
   Entrada: Solicitud de inscripción
   Proceso: Recepción → Validación documentos → Crear usuario → Enviar credenciales
   Salida: Usuario activo en sistema con rol madre_comunitaria

3. GESTIÓN DE HOGARES COMUNITARIOS
   Entrada: Necesidad de crear nuevo hogar
   Proceso: Definir datos → Ubicación → Asignar madre → Crear estructura
   Salida: Hogar operativo en sistema

4. GESTIÓN DE NIÑOS EN HOGARES
   Entrada: Nuevo niño ingresa al hogar
   Proceso: Registro datos → Crear expediente → Asignar a madre → Iniciar seguimiento
   Salida: Niño registrado con historial disponible

5. PLANEACIÓN EDUCATIVA
   Entrada: Período educativo nuevo (semanal/mensual)
   Proceso: Crear planeación → Definir dimensiones → Documentar actividades → Activar
   Salida: Planeación activa con documentación completa

6. EVALUACIÓN Y SEGUIMIENTO DEL DESARROLLO INFANTIL
   Entrada: Observaciones diarias de desarrollo
   Proceso: Registrar seguimiento → Evaluar dimensiones → Acumular historial → Generar reportes
   Salida: Evaluaciones guardadas, reportes generados

7. SOLICITUDES Y CAMBIOS DE ESTADO
   Entrada: Solicitud de matriculación / retiro
   Proceso: Crear solicitud → Validar documentos → Revisar → Aprobar/Rechazar → Notificar
   Salida: Solicitud resuelta, usuario notificado

8. COMUNICACIONES Y NOTIFICACIONES
   Entrada: Evento de negocio ocurre en sistema
   Proceso: Detectar evento → Crear notificación → Enviar email → Registrar en audit
   Salida: Usuario notificado, evento registrado

9. REPORTES Y ANÁLISIS
   Entrada: Necesidad de generar reporte
   Proceso: Seleccionar datos → Compilar información → Generar PDF → Disponibilizar
   Salida: Reporte descargable o guardado
```

---

### 2. ESTRUCTURA DE SWIMLANES DEL MAPA MAESTRO

El diagrama debe tener **5 swimlanes principales** que corresponden a los 5 módulos estratégicos:

```
┌────────────────────────────────────────────────────────────────────────┐
│                    MÓDULO 1: AUTENTICACIÓN Y ACCESO                    │
│ Procesos: Login → Validación rol → Acceso dashboard                   │
│ Actores: Usuario, Sistema, BD                                          │
│ Resultado: Usuario autenticado en su rol                               │
└────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌────────────────────────────────────────────────────────────────────────┐
│              MÓDULO 2: GESTIÓN DE USUARIOS Y ESTRUCTURA                │
│ Procesos:                                                              │
│  - Inscripción Madre Comunitaria                                       │
│  - Creación Hogares Comunitarios                                       │
│  - Asignación de responsabilidades                                     │
│ Actores: Padre, Madre, Administrador, Sistema                          │
│ Resultado: Estructura organizacional operativa                         │
└────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌────────────────────────────────────────────────────────────────────────┐
│            MÓDULO 3: GESTIÓN DE NIÑOS Y EXPEDIENTES                    │
│ Procesos:                                                              │
│  - Registro de niños                                                   │
│  - Crear expedientes                                                   │
│  - Documentación de datos personales                                   │
│ Actores: Madre Comunitaria, Sistema, Almacenamiento                    │
│ Resultado: Niños registrados con expedientes completos                 │
└────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌────────────────────────────────────────────────────────────────────────┐
│         MÓDULO 4: EDUCACIÓN Y SEGUIMIENTO DEL DESARROLLO               │
│ Procesos:                                                              │
│  - Crear planeación educativa                                          │
│  - Documentar actividades por dimensión                                │
│  - Registrar seguimiento diario                                        │
│  - Realizar evaluaciones multidimensionales                            │
│  - Generar reportes de desarrollo                                      │
│ Actores: Madre Comunitaria, Sistema, Almacenamiento                    │
│ Resultado: Seguimiento completo del desarrollo infantil                │
└────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌────────────────────────────────────────────────────────────────────────┐
│     MÓDULO 5: COMUNICACIONES, SOLICITUDES Y ANÁLISIS                   │
│ Procesos:                                                              │
│  - Gestionar solicitudes (matriculación, retiro)                       │
│  - Enviar notificaciones y emails                                      │
│  - Generar reportes analíticos                                         │
│  - Registrar auditoría                                                 │
│ Actores: Usuarios, Sistema, Email Service, Almacenamiento              │
│ Resultado: Comunicaciones efectivas, decisiones informadas             │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 3. FLUJO GENERAL DEL SISTEMA (Secuencia temporal)

El diagrama maestro debe mostrar **cuándo ocurre cada proceso** en el ciclo de vida:

```
TIMELINE DE PROCESOS:

T0 - INICIO (Usuario nuevo llega al sistema)
└─ Proceso 1: LOGIN Y AUTENTICACIÓN
   └─ Proceso 7: SOLICITUD INICIAL (si es padre)
      └─ Proceso 2: INSCRIPCIÓN MADRE (si solicitud aprobada)

T1 - CONFIGURACIÓN (Estructura lista)
└─ Proceso 3: CREAR HOGAR COMUNITARIO
   └─ Proceso 4: REGISTRAR NIÑOS EN HOGAR
      └─ MADRE COMUNITARIA LISTA PARA TRABAJAR

T2 - OPERACIÓN CONTINUA (Ciclo educativo)
└─ Proceso 5: CREAR PLANEACIÓN EDUCATIVA (semanal/mensual)
   └─ Proceso 6.1: REGISTRAR SEGUIMIENTO DIARIO
      └─ Proceso 6.2: EVALUAR DIMENSIONES (periódicamente)
         └─ Proceso 6.3: GENERAR REPORTES
            └─ Proceso 8: NOTIFICAR A PADRES (automático)

T3 - CAMBIOS (Durante operación)
└─ Proceso 7: SOLICITUDES (matriculación adicional, retiro)
   └─ Proceso 2: NUEVOS USUARIOS si aplica
   └─ Proceso 8: NOTIFICACIONES sobre cambios

T4 - SOPORTE (Continuo)
└─ Proceso 8: COMUNICACIONES
└─ Proceso 9: REPORTES Y ANÁLISIS
└─ AUDITORÍA: Todas las acciones registradas
```

---

### 4. INTERCONEXIONES ENTRE PROCESOS

El diagrama debe mostrar **cómo se comunican** los procesos:

```
PROCESO 1: LOGIN
    ├─→ PROCESO 5: Madre abre planeación
    ├─→ PROCESO 6: Padre consulta desarrollo
    └─→ PROCESO 7: Admin gestiona solicitudes

PROCESO 2: INSCRIPCIÓN MADRE
    ├─→ PROCESO 3: Asignar a hogar
    ├─→ PROCESO 8: Enviar email bienvenida
    └─→ NOTIFICACIÓN: Admin notificado

PROCESO 3: CREAR HOGAR
    ├─→ PROCESO 4: Registrar niños
    └─→ PROCESO 5: Iniciar planeación educativa

PROCESO 4: REGISTRAR NIÑO
    ├─→ PROCESO 6: Crear expediente
    ├─→ ALMACENAMIENTO: /media/ninos/{id}/
    └─→ PROCESO 8: Notificar a padre

PROCESO 5: PLANEACIÓN EDUCATIVA
    ├─→ ALMACENAMIENTO: Guardar documentos
    ├─→ PROCESO 6: Evaluar según planeación
    └─→ PROCESO 9: Datos para reportes

PROCESO 6: EVALUACIÓN Y SEGUIMIENTO
    ├─→ PROCESO 6.1: Seguimiento diario
    ├─→ PROCESO 6.2: Evaluaciones periódicas
    ├─→ PROCESO 6.3: Generar PDF
    ├─→ ALMACENAMIENTO: /media/reportes/
    └─→ PROCESO 8: Notificar a padre

PROCESO 7: SOLICITUDES
    ├─→ PROCESO 2: Si es matriculación (crear usuario)
    ├─→ PROCESO 3: Si es cambio de hogar
    ├─→ PROCESO 8: Enviar resolución
    └─→ AUDITORÍA: Registrar decisión

PROCESO 8: COMUNICACIONES
    ├─→ EMAIL SERVICE: Enviar notificación
    ├─→ NOTIFICACIÓN SISTEMA: Guardar en BD
    ├─→ EMAILLOG: Registrar intento
    └─→ AUDITORÍA: Historial de comunicaciones

PROCESO 9: REPORTES
    ├─ Fuente PROCESO 5: Datos planeación
    ├─ Fuente PROCESO 6: Datos evaluaciones
    ├─ Fuente PROCESO 7: Datos solicitudes
    └─→ ALMACENAMIENTO: Guardar PDF generado
```

---

### 5. DECISIONES CRÍTICAS EN CADA PROCESO

El diagrama debe mostrar **los gateways (puntos de decisión):**

```
PROCESO 1: LOGIN
├─ ¿Usuario existe?
├─ ¿Contraseña correcta?
└─ ¿Cuenta está activa?

PROCESO 2: INSCRIPCIÓN MADRE
├─ ¿Documentos completos?
├─ ¿Tamaños de archivo válidos?
├─ ¿Antecedentes válidos?
└─ ¿Email ya existe?

PROCESO 3: CREAR HOGAR
├─ ¿Ubicación es válida?
└─ ¿Datos completados?

PROCESO 4: REGISTRAR NIÑO
├─ ¿Niño ya existe en sistema?
└─ ¿Hogar tiene cupo?

PROCESO 5: PLANEACIÓN EDUCATIVA
├─ ¿Período no duplicado?
├─ ¿Documentación completa?
└─ ¿Dimensiones seleccionadas?

PROCESO 6: EVALUACIÓN
├─ ¿Datos completos?
├─ ¿Rango de logro válido?
└─ ¿Generar reportes? (condicional)

PROCESO 7: SOLICITUDES
├─ ¿Documentos válidos?
├─ ¿Hogar destino existe?
├─ ¿Cupo disponible?
└─ ¿Aprobar o rechazar?

PROCESO 8: COMUNICACIONES
├─ ¿Email habilitado en settings?
├─ ¿Dirección válida?
└─ ¿Registrar en EmailLog?

PROCESO 9: REPORTES
├─ ¿Período especificado?
└─ ¿Generar PDF o descargar?
```

---

## 🎨 CÓMO DEBERÍA VERSE EL DIAGRAMA MAESTRO

### Opción A: Diagrama Horizontal (Flujo left-to-right)

```
START (Usuario llega)
   ↓
[Proceso 1: Login] ──→ ◇ ¿Válido?
   ├─ Sí ──→ [Dashboard según rol]
   └─ No ──→ [Mostrar error, reintentar]

   ↓ (Usuario autenticado)

┌─────────────────────────────────────────────────────────────┐
│ FLUJO PADRE:                    FLUJO MADRE:                │
│                                                              │
│ [Ver niños a cargo]             [Gestionar hogar]           │
│      ↓                                ↓                      │
│ [Crear solicitud]  ←─────────→ [Registrar niños]           │
│      ↓                                ↓                      │
│ [Esperar aprobación]            [Crear planeación]          │
│      ↓                                ↓                      │
│ [Ver reportes desarrollo]       [Documentar actividades]    │
│      ↓                                ↓                      │
│ [Consultar evaluaciones]        [Registrar seguimiento]     │
│                                      ↓                      │
│                           [Realizar evaluaciones]           │
│                                      ↓                      │
│                           [Generar reportes]                │
│                                                              │
│             ↓─────────────────────────↓                      │
│       [Sistema envía notificaciones]                        │
│             ↓                                                │
│       [Email a todos afectados]                            │
└─────────────────────────────────────────────────────────────┘

   ↓ (Ciclo continuo)

[Solicitudes pendientes?] ──→ [Gestionar solicitudes]
         ↓                              ↓
[Aprobar/Rechazar] ──→ [Notificar]
         ↓
[Volver a Flujo principal]

   ↓

[Reportes y análisis periódicos]
         ↓
END (Sistema operativo)
```

---

### Opción B: Diagrama Vertical por Módulos

```
┌─────────────────────────────────┐
│  MÓDULO 1: AUTENTICACIÓN        │
│  ────────────────────────────    │
│  O "Usuario ingresa credenciales"│
│       ↓                          │
│  [Validar login]                 │
│       ↓                          │
│  ◇ "¿Credenciales válidas?"     │
│   ├─ Sí → [Cargar dashboard]    │
│   └─ No → [Mostrar error]       │
│       ↓                          │
└──────────────────────┬───────────┘
                       ↓ (Usuario autenticado)
┌─────────────────────────────────┐
│  MÓDULO 2: GESTIÓN ESTRUCTURA   │
│  ────────────────────────────    │
│  ◇ "¿Rol = admin?"              │
│   ├─ Sí → [Crear hogar]         │
│   │       ↓                      │
│   │     [Crear usuario madre]    │
│   │       ↓                      │
│   └─→ MÓDULO 3                  │
│   ├─ No → [Ver hogares asignados]│
│           ↓                      │
│         MÓDULO 3                 │
└──────────────────────┬───────────┘
                       ↓
┌─────────────────────────────────┐
│  MÓDULO 3: GESTIÓN DE NIÑOS     │
│  ────────────────────────────    │
│  [Seleccionar hogar]             │
│       ↓                          │
│  [Listar niños activos]          │
│       ↓                          │
│  ◇ "¿Crear nuevo niño?"         │
│   ├─ Sí → [Registrar niño]      │
│   │       ↓                      │
│   │    MÓDULO 4                  │
│   └─ No → MÓDULO 4              │
└──────────────────────┬───────────┘
                       ↓
┌─────────────────────────────────┐
│  MÓDULO 4: EDUCACIÓN Y DESARROLLO
│  ────────────────────────────    │
│  [Crear planeación educativa]    │
│       ↓                          │
│  [Documentar por dimensión]      │
│       ↓                          │
│  [Registrar seguimiento diario]  │
│       ↓                          │
│  [Realizar evaluaciones]         │
│       ↓                          │
│  [Generar reportes PDF]          │
│       ↓                          │
│    MÓDULO 5                      │
└──────────────────────┬───────────┘
                       ↓
┌─────────────────────────────────┐
│  MÓDULO 5: COMUNICACIONES        │
│  ────────────────────────────    │
│  O "Evento del sistema"          │
│       ↓                          │
│  [Crear notificación]            │
│       ↓                          │
│  ◇ "¿Enviar email?"             │
│   ├─ Sí → [Enviar vía SMTP]     │
│   │       ↓                      │
│   │   [Registrar en EmailLog]    │
│   └─ No → [Solo notificación]   │
│       ↓                          │
│  [Registrar en auditoría]        │
│       ↓                          │
│  ● "Evento completado"           │
└─────────────────────────────────┘
```

---

### Opción C: Diagrama Matricial (Procesos vs Actores)

```
                    PADRE    MADRE      ADMIN    SISTEMA    SERVICIOS
                            COMUNITARIA
LOGIN                  ✓        ✓         ✓        ✓
SOLICITAR MATRICULACIÓN ✓        -         -        ✓         EMAIL
INSCRIBIR MADRE         -        -         ✓        ✓         EMAIL
CREAR HOGAR             -        -         ✓        ✓
REGISTRAR NIÑO          -        ✓         ✓        ✓         STORAGE
CREAR PLANEACIÓN        -        ✓         -        ✓         STORAGE
DOCUMENTAR ACTIVIDADES  -        ✓         -        ✓         STORAGE
SEGUIMIENTO DIARIO      -        ✓         -        ✓
EVALUAR DIMENSIONES     -        ✓         -        ✓
GENERAR REPORTES        ✓        ✓         ✓        ✓         STORAGE
GESTIONAR SOLICITUDES   -        -         ✓        ✓         EMAIL
NOTIFICACIONES          ✓        ✓         ✓        ✓         EMAIL
AUDITORÍA               -        -         ✓        ✓
```

---

## 📐 ESTRUCTURA DETALLADA DEL DIAGRAMA MAESTRO

### Elementos Obligatorios a Mostrar:

#### **1. Swimlanes (5 principales)**
```
┌─────────────────────┐
│  ACTOR 1: PADRE     │
├─────────────────────┤
│ - Solicita          │
│ - Consulta          │
│ - Recibe reportes   │
└─────────────────────┘

┌─────────────────────┐
│  ACTOR 2: MADRE     │
├─────────────────────┤
│ - Planifica         │
│ - Documenta         │
│ - Evalúa            │
└─────────────────────┘

┌─────────────────────┐
│  ACTOR 3: ADMIN     │
├─────────────────────┤
│ - Crea estructura   │
│ - Aprueba           │
│ - Supervisa         │
└─────────────────────┘

┌─────────────────────┐
│  ACTOR 4: SISTEMA   │
├─────────────────────┤
│ - Valida            │
│ - Procesa           │
│ - Almacena          │
└─────────────────────┘

┌─────────────────────┐
│  SERVICIOS EXTERNOS │
├─────────────────────┤
│ - Email SMTP        │
│ - Filesystem        │
│ - Scheduler         │
└─────────────────────┘
```

#### **2. Eventos (Inicio y Fin)**
```
O "Usuario accede al sistema"  ← Inicio principal
O "Solicitud de inscripción"   ← Inicio alternativo
O "Período educativo nuevo"    ← Inicio ciclo educativo
O "Cambio solicitado"          ← Inicio proceso cambio

● "Sistema operativo"          ← Fin exitoso
● "Usuario en dashboard"       ← Fin exitoso parcial
● "Notificación enviada"       ← Fin exitoso proceso
● "Error - Reintentar"         ← Fin error
```

#### **3. Procesos Principales (9 con sus subprocesos)**
```
[1. LOGIN → Validar → Cargar Dashboard]
[2. INSCRIBIR → Validar docs → Crear usuario → Enviar email]
[3. CREAR HOGAR → Definir datos → Ubicación → Validar]
[4. REGISTRAR NIÑO → Datos → Expediente → Seguimiento]
[5. PLANEACIÓN → Crear → Documentar → Activar]
[6. EVALUAR → Seguimiento → Dimensiones → Reportes]
[7. SOLICITUDES → Crear → Validar → Aprobar → Notificar]
[8. COMUNICACIONES → Evento → Notif → Email → Log]
[9. REPORTES → Compilar → Generar PDF → Descargar]
```

#### **4. Decisiones Críticas (Gateways)**
```
◇ "¿Credenciales válidas?"
◇ "¿Documentos completos?"
◇ "¿Cupo disponible?"
◇ "¿Email habilitado?"
◇ ¿Datos completos?"
... etc
```

#### **5. Flujos de Comunicación Entre Procesos**
```
Proceso 2 → envía datos a → Proceso 3
Proceso 4 → envía datos a → Proceso 6
Proceso 6 → dispara → Proceso 8
Proceso 5 → proporciona contexto a → Proceso 6
Proceso 7 → puede crear → Proceso 2
Todos → generan eventos en → Proceso 8
Todos → registran en → AUDITORÍA
```

---

## 📋 VISTA GENERAL DE LOS 9 PROCESOS

El diagrama maestro debe mostrar claramente ESTOS procesos:

### **Proceso 1: INGRESO AL SISTEMA**
```
Inicio: Usuario accede a login
Actores: Usuario, Sistema
Pasos: Ingresar credenciales → Validar → Asignar rol → Cargar dashboard
Fin: Usuario autenticado en su rol
Resultado: Dashboard del usuario listo
```

### **Proceso 2: INSCRIPCIÓN MADRE COMUNITARIA**
```
Inicio: Solicitud de inscripción aprobada
Actores: Administrador, Sistema, Email Service
Pasos: Validar documentos → Crear usuario → Generar carpetas → Enviar credenciales
Fin: Usuario creado, email enviado
Resultado: Madre lista para trabajar
```

### **Proceso 3: CREAR HOGAR COMUNITARIO**
```
Inicio: Administrador decide crear hogar
Actores: Administrador, Sistema
Pasos: Completar datos → Seleccionar ubicación → Validar → Guardar
Fin: Hogar registrado
Resultado: Hogar operativo en sistema
```

### **Proceso 4: REGISTRAR NIÑO EN HOGAR**
```
Inicio: Madre registra nuevo niño
Actores: Madre Comunitaria, Sistema, Almacenamiento
Pasos: Datos personales → Crear expediente → Generar carpeta → Iniciar seguimiento
Fin: Niño registrado
Resultado: Expediente disponible, seguimiento iniciado
```

### **Proceso 5: CREAR PLANEACIÓN EDUCATIVA**
```
Inicio: Nuevo período educativo (semanal/mensual)
Actores: Madre Comunitaria, Sistema, Almacenamiento
Pasos: Nueva planeación → Seleccionar dimensiones → Documentar → Activar
Fin: Planeación activa
Resultado: Documentación disponible para evaluación
```

### **Proceso 6: EVALUACIÓN Y SEGUIMIENTO DEL DESARROLLO**
```
Inicio: Seguimiento diario o evaluación periódica
Actores: Madre Comunitaria, Sistema, Almacenamiento
Pasos: Registrar observaciones → Evaluar por dimensión → Acumular en historial → Generar reportes
Fin: Reportes disponibles
Resultado: Desarrollo del niño documentado
```

### **Proceso 7: GESTIONAR SOLICITUDES**
```
Inicio: Solicitud de matriculación, cambio o retiro
Actores: Padre/Madre/Admin, Sistema, Email Service
Pasos: Crear solicitud → Validar → Revisar → Aprobar/Rechazar → Notificar
Fin: Solicitud resuelta
Resultado: Usuario notificado del resultado
```

### **Proceso 8: COMUNICACIONES Y NOTIFICACIONES**
```
Inicio: Evento de negocio ocurre (cualquier cambio en sistema)
Actores: Sistema, Email Service, Usuarios
Pasos: Detectar evento → Crear notificación → Enviar email → Registrar log
Fin: Usuario notificado
Resultado: Comunicación efectiva
```

### **Proceso 9: GENERAR REPORTES Y ANÁLISIS**
```
Inicio: Usuario solicita reporte
Actores: Usuario, Sistema, Almacenamiento
Pasos: Seleccionar datos → Compilar → Generar PDF → Disponibilizar
Fin: Reporte descargable
Resultado: Datos para toma de decisiones
```

---

## 🔄 CICLO DE VIDA COMPLETO (Cómo se relacionan los procesos)

El diagrama debe mostrar **el viaje del usuario** a través del sistema:

```
                    CICLO DE VIDA - PADRE
                    ─────────────────────
                    
T0: Accede al sistema
    ↓
    [Proceso 1: LOGIN]
    ↓
    Dashboard de padre
    ↓
    ¿Tiene hijo en hogar?
    ├─ No → [Proceso 7: Crear solicitud de matriculación]
    │       ↓
    │       Esperar aprobación
    │       ↓
    │       Si aprobada → Hijo registrado
    │
    └─ Sí → Continuar
            ↓
    [Proceso 6.3: Ver reportes de desarrollo]
            ↓
    [Proceso 8: Recibir notificaciones de cambios]
            ↓
    [Proceso 9: Descargar reportes PDF]
            ↓
    Fin (acceso periódico)


                    CICLO DE VIDA - MADRE COMUNITARIA
                    ─────────────────────────────────
                    
T0: Primer acceso después de inscripción
    ↓
    [Proceso 1: LOGIN]
    ↓
    Dashboard de madre
    ↓
    [Proceso 3: Ver hogares asignados]
    ↓
    [Proceso 4: Registrar/Ver niños]
    ↓
    Ciclo educativo comienza (semanal/mensual)
    ├─ [Proceso 5: Crear planeación]
    ├─ [Proceso 6.1: Seguimiento diario]
    ├─ [Proceso 6.2: Evaluar dimensiones]
    └─ [Proceso 6.3: Generar reportes]
    ↓
    [Proceso 8: Notificaciones periódicas]
    ↓
    Repetir ciclo educativo
    ↓
    Si cambios: [Proceso 7: Solicitudes]
    ↓
    Fin (acceso diario)


                    CICLO DE VIDA - ADMINISTRADOR
                    ──────────────────────────────
                    
T0: Acceso al sistema
    ↓
    [Proceso 1: LOGIN con rol admin]
    ↓
    Dashboard administrativo
    ├─ [Proceso 3: Crear/Gestionar hogares]
    ├─ [Proceso 2: Gestionar inscripciones de madres]
    ├─ [Proceso 7: Revisar y aprobar solicitudes]
    ├─ [Proceso 4: Supervisar registro de niños]
    ├─ [Proceso 9: Generar reportes de supervisión]
    └─ [Proceso 8: Recibir notificaciones de eventos]
    ↓
    Auditoría de todas las acciones
    ↓
    Fin (acceso según necesidad)
```

---

## 📊 VISTAS DEL DIAGRAMA MAESTRO

El diagrama debe poder verse desde **múltiples perspectivas:**

### Vista 1: Flujo Temporal (Cuándo ocurre qué)
- Inicio (Login) → Configuración (Crear estructura) → Operación (Educación) → Cambios (Solicitudes) → Soporte (Reportes)

### Vista 2: Flujo por Rol (Qué ve cada actor)
- Padre: Login → Consulta → Recibe reportes
- Madre: Login → Planifica → Ejecuta → Evalúa → Reporta
- Admin: Login → Configura → Gestiona → Supervisa → Analiza

### Vista 3: Flujo de Datos (Qué información fluye)
- Datos de usuario → Datos de hogar → Datos de niño → Datos de seguimiento → Reportes → Comunicaciones

### Vista 4: Flujo de Decisiones (Dónde se aprueban cambios)
- Solicitud → Validación → Decisión de admin → Aprobación/Rechazo → Notificación → Acción

---

## ⚠️ ELEMENTOS QUE NO DEBE INCLUIR

❌ **Código técnico** (SQL, ORM, APIs)
❌ **Nombres de tablas de BD** (usuarios, ninos, etc)
❌ **Detalles de frameworks** (Django, xhtml2pdf, etc)
❌ **Pantallas de interfaz** (templates HTML)
❌ **Configuraciones** (.env, settings.py)
❌ **Detalles de almacenamiento de archivos** (/media/... solo si es decisión)
❌ **Decoradores y utilidades** (@rol_requerido, signals, etc)
❌ **Implementación de características** (Pillow, APScheduler)

---

## ✅ ELEMENTOS QUE SÍ DEBE INCLUIR

✅ **Los 9 procesos principales claramente identificados**
✅ **5 swimlanes de actores/módulos**
✅ **Gateways/decisiones críticas del negocio**
✅ **Flujos de comunicación entre procesos**
✅ **Eventos de inicio y fin**
✅ **Actividades con nomenclatura clara (verbo + objeto)**
✅ **Almacenamiento como actor (Filesystem, BD)**
✅ **Servicios externos (Email, Notificaciones)**
✅ **Auditoría como proceso transversal**
✅ **Ciclo completo de vida del usuario**

---

## 📐 FORMATO DE SALIDA

### **Sección 1: Estructura del Diagrama**
- Explicar la organización (módulos, swimlanes, flujos)

### **Sección 2: Descripción de Procesos**
- Los 9 procesos con: inicio, pasos, fin, resultado

### **Sección 3: Diagrama Visual**
- Mermaid (grande, multiple subgraphs)
- O ASCII art mejorado
- O referencia BPMN XML con estructura

### **Sección 4: Matriz de Responsabilidades**
- Quién participa en cada proceso

### **Sección 5: Flujos Críticos**
- Caminos principales del sistema

### **Sección 6: Integraciones**
- Cómo se comunican los procesos

### **Sección 7: Notas**
- Reglas de negocio, excepciones, consideraciones

---

## 🎯 VALIDACIÓN FINAL

El diagrama maestro **DEBE cumplir:**

```
☐ Mostrar 9 procesos principales
☐ Usar 5 swimlanes de actores
☐ Incluir todas las decisiones críticas
☐ Mostrar flujos de comunicación
☐ Ser autoexplicativo (sin documentación extra)
☐ Usar nomenclatura clara (verbo + objeto)
☐ No incluir código técnico
☐ Mostrar ciclo de vida completo
☐ BPMN 2.0 compliant
☐ ISO/IEC 19510 estándar
```

---

## 🚀 INSTRUCCIÓN FINAL

**Genera un diagrama maestro BPMN 2.0 COMPLETO del sistema ICBF Conecta que muestre:**

1. ✅ **Los 9 procesos principales interconectados**
2. ✅ **5 swimlanes de actores/módulos**
3. ✅ **Todas las decisiones críticas (gateways)**
4. ✅ **Flujos de comunicación y datos entre procesos**
5. ✅ **Ciclo de vida completo de cada tipo de usuario**
6. ✅ **Eventos de inicio y fin del sistema**
7. ✅ **Almacenamiento y servicios externos integrados**
8. ✅ **Auditoría como proceso transversal**

**El diagrama debe ser:**
- Profesional (BPMN 2.0 / ISO/IEC 19510)
- Comprensible (sin explicación adicional)
- Completo (todas las funciones del sistema)
- Realista (flujo real, no idealizado)
- Usar múltiples formatos (Mermaid + Textual + Notas)

**Antes de generar:**
- ✓ Valida que incluye todos los 9 procesos
- ✓ Valida que tiene 5 swimlanes principales
- ✓ Valida que incluye todas las decisiones
- ✓ Valida que es autoexplicativo

**NO generes hasta pasar TODAS las validaciones.**
