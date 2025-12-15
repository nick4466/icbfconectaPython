"""
URL configuration for icbfconecta project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views
from core.custom_password_reset_form import CustomPasswordResetForm
from core.forms import CustomAuthForm
from django.conf import settings   
from django.conf.urls.static import static
from django.urls import path
from core.views import calendario_padres, obtener_info






urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/',
    auth_views.LoginView.as_view(template_name='login.html',authentication_form=CustomAuthForm),name='login'),

    # --- URLs para Restablecimiento de Contraseña ---
     path(
    'reset_password/',
    auth_views.PasswordResetView.as_view(
        template_name="password_reset/password_reset_form.html",
        form_class=CustomPasswordResetForm,
        email_template_name="password_reset/password_reset_email.html",
        subject_template_name="password_reset/password_reset_subject.txt",
        html_email_template_name="password_reset/password_reset_email.html"  # 👈 ESTA ES LA QUE FALTABA
    ),
    name="password_reset"
     ),

     path(
     'reset_password_sent/',
     auth_views.PasswordResetDoneView.as_view(
          template_name="password_reset/password_reset_done.html"
     ), 
     name="password_reset_done"
     ),

     path(
     'reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(
          template_name="password_reset/password_reset_confirm.html"
     ), 
     name="password_reset_confirm"
     ),

     path(
     'reset_password_complete/',
     auth_views.PasswordResetCompleteView.as_view(
          template_name="password_reset/password_reset_complete.html"
     ), 
     name="password_reset_complete"
     ),

    # URL de Redirección por Rol (Nuevo Punto de Entrada después del Login)
    path('dashboard/', views.role_redirect, name='role_redirect'),
    
    # Dashboards
    path('dashboard/admin/', views.admin_dashboard, name='dashboard_admin'),
    path('dashboard/admin/reportes/', views.admin_reportes, name='admin_reportes'),
    path('dashboard/admin/hogares/', views.hogares_dashboard, name='hogares_dashboard'),  # Nuevo dashboard de hogares
    path('dashboard/madre/', views.madre_dashboard, name='madre_dashboard'), # Nuevo
    path('dashboard/padre/', views.padre_dashboard, name='padre_dashboard'), # Nuevo para padres
    
    # --- 🆕 APIs del Dashboard Mejorado ---
    path('api/hogares/<int:hogar_id>/detalle/', views.hogar_detalle_api, name='hogar_detalle_api'),
    path('api/hogares/<int:hogar_id>/historial-visitas/', views.hogar_historial_visitas_api, name='hogar_historial_visitas_api'),
    path('api/hogares/<int:hogar_id>/descargar-acta/', views.descargar_acta_visita, name='descargar_acta_visita'),
    path('api/ninos/<int:nino_id>/detalle/', views.nino_detalle_api, name='nino_detalle_api'),
    path('preview/<str:tipo>/<int:id>/<str:campo>/', views.preview_document, name='preview_document'),
    path('ninos/<int:nino_id>/carpeta/', views.nino_carpeta_view, name='nino_carpeta'),

    # --- Visitas Técnicas y Gestión de Hogares ---
    path('hogares/<int:hogar_id>/realizar-visita/', views.realizar_visita_tecnica, name='realizar_visita_tecnica'),
    path('hogares/<int:hogar_id>/programar-visita/', views.programar_visita, name='programar_visita'),
    path('hogares/<int:hogar_id>/activar/', views.activar_hogar, name='activar_hogar'),  # 🆕 Formulario de activación
    path('hogares/<int:hogar_id>/registrar-visita/', views.registrar_visita, name='registrar_visita'),  # 🆕 Visitas de seguimiento
    
    # 🆕 API para Sistema de Gestión de Visitas
    path('api/hogares/<int:hogar_id>/actualizar-visitas/', views.actualizar_visitas_hogar, name='actualizar_visitas_hogar'),

    # --- Vistas para Padres (Ahora con ID de niño) ---
    path('padre/desarrollo/<int:nino_id>/', views.padre_ver_desarrollo, name='padre_ver_desarrollo'),
    path('padre/asistencia/<int:nino_id>/', views.padre_historial_asistencia, name='padre_historial_asistencia'),
    path('padre/perfil-hijo/<int:nino_id>/', views.padre_perfil_hijo, name='padre_perfil_hijo'),
    path('padre/calendario/', calendario_padres, name='calendario_padres'),
    path('padre/calendario/info/', obtener_info, name='obtener_info'),

    # --- Gestión de Perfil de Usuario ---
    path('perfil/cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfil/actualizar-foto/', views.actualizar_foto_perfil, name='actualizar_foto_perfil'),

    # Logout
    # next_page='home' es correcto si 'home' es la URL de aterrizaje después de cerrar sesión
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'), 

    # --- CRUD Madres ---
    path('madres/', views.listar_madres, name='listar_madres'),
    path('hogares/', views.listar_hogares, name='listar_hogares'), # <-- NUEVA RUTA
    path('madres/crear/', views.crear_madre, name='crear_madre'),
    path('madres/editar/<int:id>/', views.editar_madre, name='editar_madre'),
    path('madres/eliminar/<int:id>/', views.eliminar_madre, name='eliminar_madre'),
    path('madres/detalles/<int:id>/', views.detalles_madre_json, name='detalles_madre_json'),
    
    # --- Reportes Excel ---
    path('reportes/administradores/excel/', views.reporte_administradores_excel, name='reporte_administradores_excel'),
    path('reportes/madres/excel/', views.reporte_madres_excel, name='reporte_madres_excel'),
    path('reportes/hogares/excel/', views.reporte_hogares_excel, name='reporte_hogares_excel'),
     path('reportes/ninos/excel/', views.reporte_ninos_excel, name='reporte_ninos_excel'),
     
    # --- CRUD Administradores ---
    path('administradores/', views.listar_administradores, name='listar_administradores'),
    path('administradores/crear/', views.crear_administrador, name='crear_administrador'),
    path('administradores/editar/<int:id>/', views.editar_administrador, name='editar_administrador'),
    path('administradores/eliminar/<int:id>/', views.eliminar_administrador, name='eliminar_administrador'),

    # --- CRUD Niños (Matrícula) ---
    path('buscar-padre/', views.buscar_padre_por_documento, name='buscar_padre'), # <-- NUEVA RUTA AJAX
    path('ninos/matricular/', views.matricular_nino, name='matricular_nino'),
    # --- 🆕 NUEVAS RUTAS PARA MEJORAS DE MATRÍCULA ---
    path('ninos/matricular-a-padre-existente/', views.matricular_nino_a_padre_existente, name='matricular_a_padre_existente'),
    path('ninos/cambiar-padre/', views.cambiar_padre_de_nino, name='cambiar_padre_nino'),
    path('ajax/buscar-padre-existente/', views.buscar_padre_ajax, name='buscar_padre_ajax'),
    path('ninos/', views.listar_ninos, name='listar_ninos'), # Para listar los niños del hogar
    path('ninos/<int:id>/ver/', views.ver_ficha_nino, name='ver_ficha_nino'),
    path('ninos/<int:id>/editar/', views.editar_nino, name='editar_nino'),
    path('ninos/<int:id>/eliminar/', views.eliminar_nino, name='eliminar_nino'),
    path('ninos/subir-documentos/', views.subir_documentos_nino, name='subir_documentos_nino'),
    path('gestion-ninos/', views.gestion_ninos, name='gestion_ninos'),
     path('ninos/<int:nino_id>/reporte_pdf/', views.reporte_matricula_nino_pdf, name='reporte_matricula_nino_pdf'),
     path('ninos/<int:nino_id>/certificado/', views.certificado_matricula_pdf, name='certificado_matricula_pdf'),
     path('ninos/reporte-general-hogar/', views.reporte_general_hogar_pdf, name='reporte_general_hogar'),
     path('ninos/reporte/', views.generar_reporte_ninos, name='generar_reporte_ninos'),

    # --- URLs Sistema de Invitaciones de Matriculación ---
    path('solicitudes/enviar-invitacion/', views.enviar_invitacion_matricula, name='enviar_invitacion_matricula'),
    path('padre/solicitar-matricula/', views.padre_solicitar_matricula, name='padre_solicitar_matricula'),
    # 🆕 URLs para que el padre gestione sus solicitudes desde el dashboard
    path('padre/solicitudes/<int:solicitud_id>/', views.padre_ver_solicitud_matricula, name='padre_ver_solicitud'),
    path('padre/solicitudes/<int:solicitud_id>/corregir/', views.padre_corregir_solicitud, name='padre_corregir_solicitud'),
    # URLs existentes
    path('solicitudes/panel-revision/', views.panel_revision_solicitudes, name='panel_revision_solicitudes'),
    path('solicitudes/pendientes/', views.listar_solicitudes_matricula, name='listar_solicitudes_matricula'),
    path('solicitudes/<int:solicitud_id>/detalle/', views.detalle_solicitud_matricula, name='detalle_solicitud_matricula'),
    path('solicitudes/<int:solicitud_id>/historial/', views.historial_solicitud, name='historial_solicitud'),
    path('solicitudes/aprobar/', views.aprobar_solicitud_matricula, name='aprobar_solicitud_matricula'),
    path('solicitudes/rechazar/', views.rechazar_solicitud_matricula, name='rechazar_solicitud_matricula'),
    path('solicitudes/correccion/', views.devolver_correccion_matricula, name='devolver_correccion_matricula'),
    path('solicitudes/eliminar/', views.eliminar_solicitud_matricula, name='eliminar_solicitud_matricula'),
    path('matricula/publico/<str:token>/', views.formulario_matricula_publico, name='formulario_matricula_publico'),
    path('matricula/publico/<str:token>/cancelar/', views.cancelar_solicitud_usuario, name='cancelar_solicitud_usuario'),

    # --- URLs de Desarrollo (Ahora en su propia app) ---
    path('desarrollo/', include('desarrollo.urls')),

    # --- URLs de Planeaciones ---
    # Se incluye el archivo de URLs de la app 'planeaciones'<--- tener encuenta para los botones dirigidos a planeaciones
    path('planeaciones/', include(('planeaciones.urls', 'planeaciones'), namespace='planeaciones')),

     # --- URLs AJAX para cargar datos geográficos dinámicamente ---
     path("ajax/cargar-ciudades/", views.cargar_ciudades, name="cargar_ciudades"),  # Para hogares (Regional→Ciudad)
     path("ajax/cargar-municipios/", views.ajax_cargar_municipios, name="ajax_cargar_municipios"),  # Departamento→Municipio
     path("ajax/cargar-localidades-bogota/", views.ajax_cargar_localidades_bogota, name="ajax_cargar_localidades_bogota"),  # Bogotá→Localidades
     
     # --- URLs AJAX para validaciones en tiempo real ---
     path("ajax/validar-nombre-hogar/", views.validar_nombre_hogar, name="validar_nombre_hogar"),  # Validar nombre hogar duplicado
     path("ajax/validar-documento-madre/", views.validar_documento_madre, name="validar_documento_madre"),  # Validar documento duplicado
     path("ajax/validar-documento-nino/", views.validar_documento_nino, name="validar_documento_nino"),  # Validar documento niño duplicado
     path("ajax/validar-correo-padre/", views.validar_correo_padre, name="validar_correo_padre"),  # Validar correo padre duplicado

     # --- URL AJAX para programar/reprogramar visitas ---
     path("ajax/programar-visita/<int:hogar_id>/", views.programar_visita_ajax, name="programar_visita_ajax"),

    # --- URLs de Visitas Técnicas ---
    path('visitas/hogares-pendientes/', views.listar_hogares_pendientes_visita, name='listar_hogares_pendientes_visita'),
    path('visitas/agendar/<int:hogar_id>/', views.agendar_visita_tecnica, name='agendar_visita_tecnica'),
    path('visitas/listar/', views.listar_visitas_tecnicas, name='listar_visitas_tecnicas'),

    # --- 🆕 URLs Formulario 2 - Sistema de Dos Fases ---
    path('hogares/revision/', views.lista_hogares_revision, name='lista_hogares_revision'),
    # Formulario eliminado - usar activar_hogar en su lugar
    # Eliminado: usar activar_hogar en su lugar
    path('hogares/<int:hogar_id>/detalle/', views.detalle_hogar, name='detalle_hogar'),

    # --- 🆕 URLs Dashboard del Padre Mejorado ---
    path('padre/hogares/', views.padre_ver_hogares, name='padre_ver_hogares'),
    path('padre/hogares/<int:hogar_id>/', views.padre_detalle_hogar, name='padre_detalle_hogar'),
    path('padre/dashboard-mejorado/', views.padre_dashboard_mejorado, name='padre_dashboard_mejorado'),

    # --- 🆕 URLs Solicitud de Retiro de Matrícula (PADRE) ---
    path('padre/solicitar-retiro/<int:nino_id>/', views.padre_solicitar_retiro, name='padre_solicitar_retiro'),
    path('padre/mis-retiros/', views.padre_ver_retiros, name='padre_ver_retiros'),
    path('padre/cancelar-retiro/<int:solicitud_id>/', views.padre_cancelar_retiro, name='padre_cancelar_retiro'),
    
    # --- 🆕 URLs Solicitudes de Matrícula (PADRE) ---
    path('padre/mis-solicitudes/', views.padre_ver_solicitudes_matricula, name='padre_solicitudes_matricula'),
    path('padre/solicitud-detalles/<int:solicitud_id>/', views.padre_solicitud_detalle, name='padre_solicitud_detalle'),

    # --- 🔔 URLs Notificaciones (PADRE) ---
    path('padre/api/notificaciones/', views.api_notificaciones_padre, name='api_notificaciones_padre'),
    path('padre/api/notificaciones/<int:notif_id>/marcar-leida/', views.api_marcar_notificacion_leida, name='api_marcar_notificacion_leida'),
    path('padre/api/notificaciones/marcar-todas-leidas/', views.api_marcar_todas_leidas, name='api_marcar_todas_leidas'),

    # --- 🆕 URLs Solicitud de Retiro de Matrícula (MADRE) ---
    path('madre/solicitudes-retiro/', views.madre_ver_retiros_solicitudes, name='madre_ver_retiros'),
    path('madre/procesar-retiro/<int:solicitud_id>/', views.madre_procesar_retiro, name='madre_procesar_retiro'),

    # --- 🆕 AJAX Barrios por Localidad ---
    path('api/barrios-por-localidad/<int:localidad_id>/', views.obtener_barrios_por_localidad, name='obtener_barrios'),
    
    # --- 🆕 AJAX Localidades Bogotá ---
    path('api/localidades-bogota/', views.api_localidades_bogota, name='api_localidades_bogota'),

    #-----------------------------------------------juanito---------------------------------------------#
    # --- URLs de Asistencias no borrar please ultra importarte ;D #---
    path('asistencia/', include('asistencia.urls')),

    path('novedades/', include('novedades.urls', namespace='novedades')),
    
    path('notifications/', include('notifications.urls')),

    
     # --- URLs de Correos Masivos ---
     path("correos/", include("correos.urls")),

    
]

# Error Handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
