"""
URL configuration for icbfconecta project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    # URL de Redirección por Rol (Nuevo Punto de Entrada después del Login)
    path('dashboard/', views.role_redirect, name='role_redirect'),
    
    # Dashboards
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/madre/', views.madre_dashboard, name='madre_dashboard'), # Nuevo
    
    # Logout
    # next_page='home' es correcto si 'home' es la URL de aterrizaje después de cerrar sesión
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'), 

    # --- CRUD Madres ---
    path('madres/', views.listar_madres, name='listar_madres'),
    path('madres/crear/', views.crear_madre, name='crear_madre'),
    path('madres/editar/<int:id>/', views.editar_madre, name='editar_madre'),
    path('madres/eliminar/<int:id>/', views.eliminar_madre, name='eliminar_madre'),

    # --- CRUD Administradores ---
    path('administradores/', views.listar_administradores, name='listar_administradores'),
    path('administradores/crear/', views.crear_administrador, name='crear_administrador'),
    path('administradores/editar/<int:id>/', views.editar_administrador, name='editar_administrador'),
    path('administradores/eliminar/<int:id>/', views.eliminar_administrador, name='eliminar_administrador'),

    # --- CRUD Niños (Matrícula) ---
    path('ninos/matricular/', views.matricular_nino, name='matricular_nino'),
    path('ninos/', views.listar_ninos, name='listar_ninos'), # Para listar los niños del hogar
]