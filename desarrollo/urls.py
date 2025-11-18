from django.urls import path
from . import views

# Define un espacio de nombres para esta aplicación.
# Esto nos permite usar {% url 'desarrollo:listar_desarrollos' %} en las plantillas.
app_name = 'desarrollo'

urlpatterns = [
    # --- URLs para la Madre Comunitaria ---
    path('registrar/', views.registrar_desarrollo, name='registrar_desarrollo'),
    path('listado/', views.listar_desarrollos, name='listar_desarrollos'),
    path('editar/<int:id>/', views.editar_desarrollo, name='editar_desarrollo'),
    path('eliminar/<int:id>/', views.eliminar_desarrollo, name='eliminar_desarrollo'),

    # --- URL para el Padre de Familia ---
    path('ver/<int:nino_id>/', views.padre_ver_desarrollo, name='padre_ver_desarrollo'),

    # --- URLs para Reportes ---
    path('reporte/resumen/<int:nino_id>/', views.reporte_resumen, name='reporte_resumen'),
    path('reporte/pdf/<int:nino_id>/', views.generar_reporte_pdf, name='generar_reporte_pdf'),
]