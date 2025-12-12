-- ========================================
-- ICBF CONECTA - ESTRUCTURA DE BASE DE DATOS
-- Sistema de Gestión de Hogares Comunitarios
-- Generado: 11 de diciembre de 2025
-- ========================================

-- ========================================
-- TABLAS DE CATÁLOGO Y CONFIGURACIÓN
-- ========================================

-- Tabla: Roles del sistema
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_rol VARCHAR(30) NOT NULL UNIQUE CHECK(nombre_rol IN ('administrador', 'madre_comunitaria', 'padre'))
);

-- Tabla: Discapacidades
CREATE TABLE discapacidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla: Regionales
CREATE TABLE regionales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla: Ciudades
CREATE TABLE ciudades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(120) NOT NULL,
    regional_id INTEGER NOT NULL,
    FOREIGN KEY (regional_id) REFERENCES regionales(id) ON DELETE CASCADE
);

-- ========================================
-- GEOGRAFÍA DE COLOMBIA
-- ========================================

-- Tabla: Departamentos
CREATE TABLE departamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    codigo VARCHAR(10) UNIQUE
);

-- Tabla: Municipios
CREATE TABLE municipios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(150) NOT NULL,
    departamento_id INTEGER NOT NULL,
    codigo VARCHAR(10),
    es_capital BOOLEAN DEFAULT 0,
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id) ON DELETE CASCADE,
    UNIQUE(nombre, departamento_id)
);

-- Tabla: Localidades de Bogotá
CREATE TABLE localidades_bogota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    numero INTEGER NOT NULL UNIQUE CHECK(numero BETWEEN 1 AND 20)
);

-- ========================================
-- USUARIOS Y PERFILES
-- ========================================

-- Tabla: Usuarios (AbstractUser personalizado)
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME,
    is_superuser BOOLEAN DEFAULT 0,
    is_staff BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    date_joined DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Campos personalizados
    tipo_documento VARCHAR(5) NOT NULL DEFAULT 'CC' CHECK(tipo_documento IN ('CC', 'TI', 'CE', 'PA')),
    documento BIGINT NOT NULL UNIQUE,
    nombres VARCHAR(50) NOT NULL,
    apellidos VARCHAR(50) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    sexo VARCHAR(1) DEFAULT 'F' CHECK(sexo IN ('M', 'F', 'O')),
    
    -- Ubicación geográfica
    departamento_residencia_id INTEGER,
    ciudad_residencia_id INTEGER,
    localidad_bogota_id INTEGER,
    direccion VARCHAR(100),
    barrio VARCHAR(100),
    
    telefono VARCHAR(20),
    nivel_educativo VARCHAR(50),
    rol_id INTEGER,
    foto_admin VARCHAR(100),
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE PROTECT,
    FOREIGN KEY (departamento_residencia_id) REFERENCES departamentos(id) ON DELETE SET NULL,
    FOREIGN KEY (ciudad_residencia_id) REFERENCES municipios(id) ON DELETE SET NULL,
    FOREIGN KEY (localidad_bogota_id) REFERENCES localidades_bogota(id) ON DELETE SET NULL
);

-- Índices para usuarios
CREATE INDEX idx_usuarios_documento ON usuarios(documento);
CREATE INDEX idx_usuarios_correo ON usuarios(correo);
CREATE INDEX idx_usuarios_rol ON usuarios(rol_id);

-- Tabla: Perfiles de Padres/Tutores
CREATE TABLE padres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL UNIQUE,
    ocupacion VARCHAR(50),
    otra_ocupacion VARCHAR(50),
    estrato INTEGER CHECK(estrato BETWEEN 1 AND 6),
    telefono_contacto_emergencia VARCHAR(20),
    nombre_contacto_emergencia VARCHAR(100),
    situacion_economica_hogar VARCHAR(100),
    documento_identidad_img VARCHAR(255),
    clasificacion_sisben VARCHAR(50),
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla: Perfiles de Madres Comunitarias
CREATE TABLE madres_comunitarias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL UNIQUE,
    
    -- Información académica
    nivel_escolaridad VARCHAR(100) NOT NULL CHECK(nivel_escolaridad IN ('Primaria', 'Bachiller', 'Técnico', 'Tecnólogo', 'Profesional')),
    titulo_obtenido VARCHAR(150),
    institucion VARCHAR(150),
    experiencia_previa TEXT,
    certificado_laboral VARCHAR(100),
    
    -- Declaraciones
    no_retirado_icbf BOOLEAN DEFAULT 0,
    carta_disponibilidad VARCHAR(100),
    firma_digital VARCHAR(100),
    foto_madre VARCHAR(100),
    
    -- Documentos soporte
    documento_identidad_pdf VARCHAR(100),
    certificado_escolaridad_pdf VARCHAR(100),
    certificado_antecedentes_pdf VARCHAR(100),
    certificado_medico_pdf VARCHAR(100),
    certificado_residencia_pdf VARCHAR(100),
    cartas_recomendacion_pdf VARCHAR(100),
    
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ========================================
-- HOGARES COMUNITARIOS
-- ========================================

-- Tabla: Hogares Comunitarios
CREATE TABLE hogares_comunitarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regional_id INTEGER NOT NULL,
    ciudad_id INTEGER NOT NULL,
    nombre_hogar VARCHAR(100) NOT NULL,
    direccion VARCHAR(200) NOT NULL,
    localidad VARCHAR(100) DEFAULT '',
    localidad_bogota_id INTEGER,
    barrio VARCHAR(100),
    estrato INTEGER,
    
    -- Visitas y estado de aptitud
    fecha_primera_visita DATE,
    ultima_visita DATE,
    proxima_visita DATE,
    observaciones_visita TEXT,
    estado_aptitud VARCHAR(20) DEFAULT 'no_apto' CHECK(estado_aptitud IN ('no_apto', 'apto')),
    
    -- Formulario 2 - Visita Técnica
    area_social_m2 DECIMAL(6,2),
    capacidad_calculada INTEGER,
    formulario_completo BOOLEAN DEFAULT 0,
    
    -- Infraestructura
    num_habitaciones INTEGER,
    num_banos INTEGER,
    material_construccion TEXT,
    riesgos_cercanos TEXT,
    
    -- Fotos y geolocalización
    fotos_interior VARCHAR(100),
    fotos_exterior VARCHAR(100),
    geolocalizacion_lat DECIMAL(10,7),
    geolocalizacion_lon DECIMAL(10,7),
    
    -- Tenencia del inmueble
    tipo_tenencia VARCHAR(50) CHECK(tipo_tenencia IN ('Propia', 'Arrendada', 'Comodato')),
    documento_tenencia_pdf VARCHAR(100),
    
    -- Capacidad
    capacidad INTEGER,
    capacidad_maxima INTEGER DEFAULT 15,
    
    -- Estado del hogar
    estado VARCHAR(30) DEFAULT 'pendiente_revision' CHECK(estado IN (
        'pendiente_revision', 'en_revision', 'aprobado', 'rechazado', 'en_mantenimiento',
        'pendiente_visita', 'visita_agendada', 'en_evaluacion', 'activo', 'inactivo'
    )),
    
    madre_id INTEGER NOT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_habilitacion DATETIME,
    
    FOREIGN KEY (regional_id) REFERENCES regionales(id) ON DELETE PROTECT,
    FOREIGN KEY (ciudad_id) REFERENCES ciudades(id) ON DELETE PROTECT,
    FOREIGN KEY (localidad_bogota_id) REFERENCES localidades_bogota(id) ON DELETE SET NULL,
    FOREIGN KEY (madre_id) REFERENCES madres_comunitarias(id) ON DELETE PROTECT
);

-- Índices para hogares
CREATE INDEX idx_hogares_regional ON hogares_comunitarios(regional_id);
CREATE INDEX idx_hogares_ciudad ON hogares_comunitarios(ciudad_id);
CREATE INDEX idx_hogares_madre ON hogares_comunitarios(madre_id);
CREATE INDEX idx_hogares_estado ON hogares_comunitarios(estado);

-- Tabla: Convivientes del Hogar
CREATE TABLE convivientes_hogar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hogar_id INTEGER NOT NULL,
    tipo_documento VARCHAR(2) DEFAULT 'CC' CHECK(tipo_documento IN ('CC', 'TI', 'CE', 'PA', 'RC')),
    numero_documento VARCHAR(20) NOT NULL,
    nombre_completo VARCHAR(200) NOT NULL,
    parentesco VARCHAR(50) NOT NULL,
    antecedentes_pdf VARCHAR(100),
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Campos legacy
    nombre VARCHAR(100),
    cedula BIGINT,
    edad INTEGER,
    
    FOREIGN KEY (hogar_id) REFERENCES hogares_comunitarios(id) ON DELETE CASCADE
);

-- ========================================
-- NIÑOS Y MATRÍCULA
-- ========================================

-- Tabla: Niños
CREATE TABLE ninos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombres VARCHAR(50) NOT NULL,
    apellidos VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    tipo_documento VARCHAR(2) DEFAULT 'RC' CHECK(tipo_documento IN ('RC', 'TI', 'CV', 'AN', 'CE', 'PA')),
    documento BIGINT,
    genero VARCHAR(20) CHECK(genero IN ('masculino', 'femenino', 'otro', 'no_especificado')),
    tipo_sangre VARCHAR(3) CHECK(tipo_sangre IN ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-')),
    parentesco VARCHAR(20) CHECK(parentesco IN ('padre', 'madre', 'tutor', 'abuelo', 'tio', 'hermano', 'otro')),
    tiene_discapacidad BOOLEAN DEFAULT 0,
    otra_discapacidad VARCHAR(100),
    nacionalidad VARCHAR(50),
    otro_pais VARCHAR(50),
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE,
    hogar_id INTEGER NOT NULL,
    padre_id INTEGER NOT NULL,
    
    -- Documentos
    foto VARCHAR(100),
    carnet_vacunacion VARCHAR(100),
    certificado_eps VARCHAR(100),
    registro_civil_img VARCHAR(100),
    
    -- Información adicional
    observaciones_medicas TEXT,
    estado VARCHAR(20) DEFAULT 'activo' CHECK(estado IN ('activo', 'inactivo', 'retirado')),
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (hogar_id) REFERENCES hogares_comunitarios(id) ON DELETE PROTECT,
    FOREIGN KEY (padre_id) REFERENCES padres(id) ON DELETE CASCADE
);

-- Tabla de relación: Niños - Discapacidades (Many-to-Many)
CREATE TABLE ninos_discapacidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nino_id INTEGER NOT NULL,
    discapacidad_id INTEGER NOT NULL,
    FOREIGN KEY (nino_id) REFERENCES ninos(id) ON DELETE CASCADE,
    FOREIGN KEY (discapacidad_id) REFERENCES discapacidades(id) ON DELETE CASCADE,
    UNIQUE(nino_id, discapacidad_id)
);

-- Índices para niños
CREATE INDEX idx_ninos_hogar ON ninos(hogar_id);
CREATE INDEX idx_ninos_padre ON ninos(padre_id);
CREATE INDEX idx_ninos_estado ON ninos(estado);

-- ========================================
-- SOLICITUDES DE MATRICULACIÓN
-- ========================================

-- Tabla: Solicitudes de Matriculación
CREATE TABLE solicitudes_matriculacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hogar_id INTEGER NOT NULL,
    email_acudiente VARCHAR(100) NOT NULL,
    token VARCHAR(100) NOT NULL UNIQUE,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion DATETIME NOT NULL,
    estado VARCHAR(30) DEFAULT 'pendiente' CHECK(estado IN (
        'pendiente', 'aprobado', 'rechazado', 'correccion', 
        'cancelado_expiracion', 'cancelado_usuario', 'token_usado'
    )),
    
    -- Tipo de solicitud
    tipo_solicitud VARCHAR(30) DEFAULT 'invitacion_madre' CHECK(tipo_solicitud IN ('invitacion_madre', 'solicitud_padre')),
    padre_solicitante_id INTEGER,
    cupos_validados BOOLEAN DEFAULT 0,
    tiene_cupos_disponibles BOOLEAN DEFAULT 0,
    
    -- Datos del niño
    nombres_nino VARCHAR(100),
    apellidos_nino VARCHAR(100),
    documento_nino VARCHAR(50),
    fecha_nacimiento_nino DATE,
    genero_nino VARCHAR(20),
    tipo_sangre_nino VARCHAR(5),
    parentesco VARCHAR(50),
    observaciones_nino TEXT,
    
    -- Discapacidad
    tiene_discapacidad BOOLEAN DEFAULT 0,
    tipos_discapacidad TEXT, -- JSON
    otra_discapacidad VARCHAR(100),
    
    -- Documentos del niño
    foto_nino VARCHAR(100),
    carnet_vacunacion_nino VARCHAR(100),
    certificado_eps_nino VARCHAR(100),
    registro_civil_nino VARCHAR(100),
    
    -- Datos del padre
    tipo_documento_padre VARCHAR(5),
    documento_padre VARCHAR(50),
    nombres_padre VARCHAR(100),
    apellidos_padre VARCHAR(100),
    correo_padre VARCHAR(100),
    telefono_padre VARCHAR(20),
    
    -- Ubicación del padre
    departamento_padre_id INTEGER,
    ciudad_padre_id INTEGER,
    localidad_bogota_padre_id INTEGER,
    direccion_padre VARCHAR(200),
    barrio_padre VARCHAR(100),
    
    ocupacion_padre VARCHAR(100),
    nivel_educativo_padre VARCHAR(50),
    password_padre VARCHAR(255),
    
    -- Documentos del padre
    documento_identidad_padre VARCHAR(100),
    clasificacion_sisben_padre VARCHAR(100),
    
    -- Corrección y rechazo
    campos_corregir TEXT, -- JSON
    motivo_rechazo TEXT,
    intentos_correccion INTEGER DEFAULT 0,
    
    -- Fechas de seguimiento
    fecha_aprobacion DATETIME,
    fecha_rechazo DATETIME,
    fecha_cancelacion DATETIME,
    motivo_cancelacion TEXT,
    
    FOREIGN KEY (hogar_id) REFERENCES hogares_comunitarios(id) ON DELETE CASCADE,
    FOREIGN KEY (padre_solicitante_id) REFERENCES padres(id) ON DELETE CASCADE,
    FOREIGN KEY (departamento_padre_id) REFERENCES departamentos(id) ON DELETE SET NULL,
    FOREIGN KEY (ciudad_padre_id) REFERENCES municipios(id) ON DELETE SET NULL,
    FOREIGN KEY (localidad_bogota_padre_id) REFERENCES localidades_bogota(id) ON DELETE SET NULL
);

-- Índices para solicitudes
CREATE INDEX idx_solicitudes_hogar ON solicitudes_matriculacion(hogar_id);
CREATE INDEX idx_solicitudes_token ON solicitudes_matriculacion(token);
CREATE INDEX idx_solicitudes_estado ON solicitudes_matriculacion(estado);
CREATE INDEX idx_solicitudes_fecha ON solicitudes_matriculacion(fecha_creacion);

-- ========================================
-- VISITAS TÉCNICAS
-- ========================================

-- Tabla: Visitas Técnicas
CREATE TABLE visitas_tecnicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hogar_id INTEGER NOT NULL,
    fecha_programada DATETIME NOT NULL,
    visitador_id INTEGER,
    estado VARCHAR(20) DEFAULT 'agendada' CHECK(estado IN ('agendada', 'en_proceso', 'completada', 'cancelada', 'reprogramada')),
    tipo_visita VARCHAR(3) DEFAULT 'V1' CHECK(tipo_visita IN ('V1', 'V2', 'V3')),
    observaciones_agenda TEXT,
    fecha_realizacion DATETIME,
    correo_enviado BOOLEAN DEFAULT 0,
    fecha_envio_correo DATETIME,
    creado_por_id INTEGER,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (hogar_id) REFERENCES hogares_comunitarios(id) ON DELETE CASCADE,
    FOREIGN KEY (visitador_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (creado_por_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- Tabla: Actas de Visitas Técnicas
CREATE TABLE actas_visitas_tecnicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visita_id INTEGER NOT NULL UNIQUE,
    
    -- Geolocalización
    geolocalizacion_lat_verificada DECIMAL(10,7) NOT NULL,
    geolocalizacion_lon_verificada DECIMAL(10,7) NOT NULL,
    direccion_verificada VARCHAR(200) NOT NULL,
    direccion_coincide BOOLEAN DEFAULT 0,
    observaciones_direccion TEXT,
    estrato_verificado INTEGER NOT NULL CHECK(estrato_verificado BETWEEN 1 AND 6),
    estrato_coincide BOOLEAN DEFAULT 0,
    foto_recibo_servicio VARCHAR(100) NOT NULL,
    
    -- Servicios básicos
    tiene_agua_potable BOOLEAN DEFAULT 0,
    agua_continua BOOLEAN DEFAULT 0,
    agua_legal BOOLEAN DEFAULT 0,
    tiene_energia BOOLEAN DEFAULT 0,
    energia_continua BOOLEAN DEFAULT 0,
    energia_legal BOOLEAN DEFAULT 0,
    tiene_alcantarillado BOOLEAN DEFAULT 0,
    manejo_excretas_adecuado BOOLEAN DEFAULT 0,
    
    -- Infraestructura
    estado_pisos VARCHAR(15) NOT NULL CHECK(estado_pisos IN ('excelente', 'bueno', 'regular', 'malo', 'muy_malo')),
    estado_paredes VARCHAR(15) NOT NULL CHECK(estado_paredes IN ('excelente', 'bueno', 'regular', 'malo', 'muy_malo')),
    estado_techos VARCHAR(15) NOT NULL CHECK(estado_techos IN ('excelente', 'bueno', 'regular', 'malo', 'muy_malo')),
    ventilacion_adecuada BOOLEAN DEFAULT 0,
    iluminacion_natural_adecuada BOOLEAN DEFAULT 0,
    observaciones_infraestructura TEXT,
    
    -- Riesgos
    proximidad_rios BOOLEAN DEFAULT 0,
    proximidad_deslizamientos BOOLEAN DEFAULT 0,
    proximidad_trafico_intenso BOOLEAN DEFAULT 0,
    proximidad_contaminacion BOOLEAN DEFAULT 0,
    nivel_riesgo_general VARCHAR(20) DEFAULT 'sin_riesgo' CHECK(nivel_riesgo_general IN ('sin_riesgo', 'riesgo_bajo', 'riesgo_medio', 'riesgo_alto', 'riesgo_critico')),
    descripcion_riesgos TEXT,
    
    -- Espacios
    area_social_largo DECIMAL(5,2) NOT NULL,
    area_social_ancho DECIMAL(5,2) NOT NULL,
    area_social_total DECIMAL(7,2),
    foto_area_social_medidas VARCHAR(100) NOT NULL,
    tiene_patio_cubierto BOOLEAN DEFAULT 0,
    patio_largo DECIMAL(5,2),
    patio_ancho DECIMAL(5,2),
    patio_total DECIMAL(7,2),
    foto_patio_medidas VARCHAR(100),
    
    -- Baños
    num_banos_verificado INTEGER NOT NULL CHECK(num_banos_verificado >= 1),
    estado_higiene_banos VARCHAR(15) NOT NULL CHECK(estado_higiene_banos IN ('excelente', 'bueno', 'aceptable', 'deficiente', 'inaceptable')),
    foto_bano_1 VARCHAR(100) NOT NULL,
    foto_bano_2 VARCHAR(100),
    
    -- Fachada
    foto_fachada VARCHAR(100) NOT NULL,
    foto_fachada_numeracion VARCHAR(100),
    
    -- Capacidad
    capacidad_calculada INTEGER,
    capacidad_recomendada INTEGER NOT NULL,
    justificacion_capacidad TEXT,
    
    -- Resultado
    resultado_visita VARCHAR(30) NOT NULL CHECK(resultado_visita IN ('aprobado', 'aprobado_condiciones', 'rechazado', 'requiere_segunda_visita')),
    observaciones_generales TEXT NOT NULL,
    recomendaciones TEXT,
    condiciones_aprobacion TEXT,
    
    -- Firmas
    firma_visitador VARCHAR(100),
    firma_madre VARCHAR(100),
    
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completado_por_id INTEGER,
    
    FOREIGN KEY (visita_id) REFERENCES visitas_tecnicas(id) ON DELETE CASCADE,
    FOREIGN KEY (completado_por_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- ========================================
-- ASISTENCIA Y ACTIVIDADES
-- ========================================

-- Tabla: Asistencia
CREATE TABLE asistencia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nino_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    estado VARCHAR(20) NOT NULL CHECK(estado IN ('Presente', 'Ausente', 'Justificado')),
    
    FOREIGN KEY (nino_id) REFERENCES ninos(id) ON DELETE CASCADE
);

CREATE INDEX idx_asistencia_nino ON asistencia(nino_id);
CREATE INDEX idx_asistencia_fecha ON asistencia(fecha);

-- ========================================
-- PLANEACIONES
-- ========================================

-- Tabla: Dimensiones
CREATE TABLE planeaciones_dimension (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL
);

-- Tabla: Planeaciones
CREATE TABLE planeaciones_planeacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    madre_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    nombre_experiencia VARCHAR(200) NOT NULL,
    intencionalidad_pedagogica TEXT NOT NULL,
    materiales_utilizar TEXT NOT NULL,
    ambiente_educativo TEXT NOT NULL,
    experiencia_inicio TEXT NOT NULL,
    experiencia_pedagogica TEXT NOT NULL,
    cierre_experiencia TEXT NOT NULL,
    situaciones_presentadas TEXT NOT NULL,
    
    FOREIGN KEY (madre_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla de relación: Planeaciones - Dimensiones (Many-to-Many)
CREATE TABLE planeaciones_planeacion_dimensiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planeacion_id INTEGER NOT NULL,
    dimension_id INTEGER NOT NULL,
    FOREIGN KEY (planeacion_id) REFERENCES planeaciones_planeacion(id) ON DELETE CASCADE,
    FOREIGN KEY (dimension_id) REFERENCES planeaciones_dimension(id) ON DELETE CASCADE,
    UNIQUE(planeacion_id, dimension_id)
);

-- Tabla: Documentación de Planeaciones
CREATE TABLE planeaciones_documentacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planeacion_id INTEGER NOT NULL,
    imagen VARCHAR(100) NOT NULL,
    
    FOREIGN KEY (planeacion_id) REFERENCES planeaciones_planeacion(id) ON DELETE CASCADE
);

-- ========================================
-- NOVEDADES
-- ========================================

-- Tabla: Novedades
CREATE TABLE novedades_novedad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nino_id INTEGER NOT NULL,
    docente VARCHAR(100) NOT NULL,
    fecha DATE NOT NULL,
    clase VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    causa VARCHAR(255),
    disposicion TEXT,
    acuerdos TEXT,
    observaciones TEXT,
    usuario_id INTEGER,
    archivo_pdf VARCHAR(100),
    tipo VARCHAR(1) NOT NULL CHECK(tipo IN ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j')),
    
    FOREIGN KEY (nino_id) REFERENCES ninos(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ========================================
-- DESARROLLO DE NIÑOS
-- ========================================

-- Tabla: Desarrollo de Niños (Evaluación Mensual)
CREATE TABLE desarrollo_desarrollonino (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nino_id INTEGER NOT NULL,
    fecha_fin_mes DATE NOT NULL,
    
    -- Indicadores Cualitativos del Mes (Automáticos)
    logro_mes VARCHAR(20) CHECK(logro_mes IN ('Alto', 'Adecuado', 'En Proceso')),
    tendencia_valoracion VARCHAR(20) CHECK(tendencia_valoracion IN ('Avanza', 'Retrocede', 'Se Mantiene', 'Sin datos previos')),
    participacion_frecuente VARCHAR(50),
    porcentaje_asistencia INTEGER,
    comportamiento_frecuente VARCHAR(50),
    
    -- Evaluación por Áreas del Desarrollo (Automática)
    evaluacion_cognitiva TEXT,
    evaluacion_comunicativa TEXT,
    evaluacion_socio_afectiva TEXT,
    evaluacion_corporal TEXT,
    evaluacion_autonomia TEXT,
    
    -- Fortalezas, Aspectos a Mejorar y Alertas (Automáticos)
    fortalezas_mes TEXT,
    aspectos_a_mejorar TEXT,
    alertas_mes TEXT,
    
    -- Conclusión General (Automática)
    conclusion_general TEXT,
    
    -- Campos Manuales (Opcionales)
    observaciones_adicionales TEXT,
    recomendaciones_personales TEXT,
    
    FOREIGN KEY (nino_id) REFERENCES ninos(id) ON DELETE CASCADE,
    UNIQUE(nino_id, fecha_fin_mes)
);

CREATE INDEX idx_desarrollo_nino ON desarrollo_desarrollonino(nino_id);
CREATE INDEX idx_desarrollo_fecha ON desarrollo_desarrollonino(fecha_fin_mes);

-- Tabla: Seguimiento Diario
CREATE TABLE desarrollo_seguimientodiario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nino_id INTEGER NOT NULL,
    planeacion_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    
    -- Campos de seguimiento
    comportamiento_general VARCHAR(20) CHECK(comportamiento_general IN (
        'participativo', 'aislado', 'impulsivo', 'inquieto', 'tranquilo', 'colaborativo'
    )),
    estado_emocional VARCHAR(20) CHECK(estado_emocional IN (
        'alegre', 'tranquilo', 'curioso', 'motivado', 'carinoso', 
        'cansado', 'triste', 'ansioso', 'frustrado', 'enojado', 
        'timido', 'aislado_emocional'
    )),
    observaciones TEXT,
    observacion_relevante BOOLEAN DEFAULT 0,
    valoracion INTEGER CHECK(valoracion BETWEEN 1 AND 5),
    
    FOREIGN KEY (nino_id) REFERENCES ninos(id) ON DELETE CASCADE,
    FOREIGN KEY (planeacion_id) REFERENCES planeaciones_planeacion(id) ON DELETE CASCADE,
    UNIQUE(nino_id, fecha)
);

CREATE INDEX idx_seguimiento_nino ON desarrollo_seguimientodiario(nino_id);
CREATE INDEX idx_seguimiento_fecha ON desarrollo_seguimientodiario(fecha);
CREATE INDEX idx_seguimiento_planeacion ON desarrollo_seguimientodiario(planeacion_id);

-- Tabla: Evaluación de Dimensiones (por seguimiento diario)
CREATE TABLE desarrollo_evaluaciondimension (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seguimiento_id INTEGER NOT NULL,
    dimension_id INTEGER NOT NULL,
    desempeno VARCHAR(10) NOT NULL CHECK(desempeno IN ('alto', 'adecuado', 'proceso', 'bajo')),
    observacion TEXT,
    
    FOREIGN KEY (seguimiento_id) REFERENCES desarrollo_seguimientodiario(id) ON DELETE CASCADE,
    FOREIGN KEY (dimension_id) REFERENCES planeaciones_dimension(id) ON DELETE CASCADE,
    UNIQUE(seguimiento_id, dimension_id)
);

CREATE INDEX idx_evaluacion_seguimiento ON desarrollo_evaluaciondimension(seguimiento_id);
CREATE INDEX idx_evaluacion_dimension ON desarrollo_evaluaciondimension(dimension_id);

-- ========================================
-- SISTEMA DE NOTIFICACIONES
-- ========================================

-- Tabla: Django Content Type (necesaria para GenericForeignKey)
CREATE TABLE django_content_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

-- Tabla: Notificaciones
CREATE TABLE notifications_notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient_id INTEGER,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    level VARCHAR(20) DEFAULT 'info' CHECK(level IN ('grave', 'warning', 'info')),
    read BOOLEAN DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Campos para GenericForeignKey
    content_type_id INTEGER,
    object_id INTEGER,
    
    FOREIGN KEY (recipient_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_recipient ON notifications_notification(recipient_id);
CREATE INDEX idx_notifications_read ON notifications_notification(read);
CREATE INDEX idx_notifications_created ON notifications_notification(created_at);
CREATE INDEX idx_notifications_content_type ON notifications_notification(content_type_id, object_id);

-- ========================================
-- CORREOS Y ARCHIVOS ADJUNTOS
-- ========================================

-- Tabla: Archivos Adjuntos de Correos
CREATE TABLE correos_archivoadjunto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    archivo VARCHAR(100) NOT NULL,
    nombre_original VARCHAR(255) NOT NULL,
    fecha_subida DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Log de Correos Enviados
CREATE TABLE correos_emaillog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asunto VARCHAR(255) NOT NULL,
    destinatarios TEXT NOT NULL,
    cuerpo TEXT NOT NULL,
    enviado_con_exito BOOLEAN DEFAULT 1,
    nota_error TEXT,
    fecha_envio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de relación: EmailLog - ArchivoAdjunto (Many-to-Many)
CREATE TABLE correos_emaillog_adjuntos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emaillog_id INTEGER NOT NULL,
    archivoadjunto_id INTEGER NOT NULL,
    FOREIGN KEY (emaillog_id) REFERENCES correos_emaillog(id) ON DELETE CASCADE,
    FOREIGN KEY (archivoadjunto_id) REFERENCES correos_archivoadjunto(id) ON DELETE CASCADE,
    UNIQUE(emaillog_id, archivoadjunto_id)
);

-- ========================================
-- HISTORIAL Y AUDITORÍA
-- ========================================

-- Tabla: Historial de Cambios
CREATE TABLE historial_cambios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_modelo VARCHAR(20) NOT NULL CHECK(tipo_modelo IN ('solicitud', 'nino', 'padre')),
    objeto_id INTEGER NOT NULL,
    campo_modificado VARCHAR(100) NOT NULL,
    valor_anterior TEXT,
    valor_nuevo TEXT,
    accion VARCHAR(50) DEFAULT 'modificacion',
    usuario_id INTEGER,
    fecha_cambio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

CREATE INDEX idx_historial_tipo_objeto ON historial_cambios(tipo_modelo, objeto_id);
CREATE INDEX idx_historial_fecha ON historial_cambios(fecha_cambio);

-- ========================================
-- DATOS INICIALES REQUERIDOS
-- ========================================

-- Insertar roles del sistema
INSERT INTO roles (nombre_rol) VALUES 
    ('administrador'),
    ('madre_comunitaria'),
    ('padre');

-- Insertar departamentos principales
INSERT INTO departamentos (nombre, codigo) VALUES
    ('Bogotá D.C.', '11'),
    ('Antioquia', '05'),
    ('Valle del Cauca', '76'),
    ('Atlántico', '08'),
    ('Santander', '68'),
    ('Cundinamarca', '25');

-- Insertar localidades de Bogotá
INSERT INTO localidades_bogota (numero, nombre) VALUES
    (1, 'Usaquén'),
    (2, 'Chapinero'),
    (3, 'Santa Fe'),
    (4, 'San Cristóbal'),
    (5, 'Usme'),
    (6, 'Tunjuelito'),
    (7, 'Bosa'),
    (8, 'Kennedy'),
    (9, 'Fontibón'),
    (10, 'Engativá'),
    (11, 'Suba'),
    (12, 'Barrios Unidos'),
    (13, 'Teusaquillo'),
    (14, 'Los Mártires'),
    (15, 'Antonio Nariño'),
    (16, 'Puente Aranda'),
    (17, 'La Candelaria'),
    (18, 'Rafael Uribe Uribe'),
    (19, 'Ciudad Bolívar'),
    (20, 'Sumapaz');

-- Insertar regional de Bogotá
INSERT INTO regionales (nombre) VALUES ('Bogotá');

-- Insertar ciudad de Bogotá
INSERT INTO ciudades (nombre, regional_id) VALUES 
    ('Bogotá', (SELECT id FROM regionales WHERE nombre = 'Bogotá'));

-- Insertar discapacidades más comunes
INSERT INTO discapacidades (nombre) VALUES
    ('Visual'),
    ('Auditiva'),
    ('Física o Motora'),
    ('Cognitiva o Intelectual'),
    ('Psicosocial o Mental'),
    ('Múltiple'),
    ('Sordoceguera'),
    ('Autismo'),
    ('Otra');

-- ========================================
-- FIN DEL SCRIPT
-- ========================================
