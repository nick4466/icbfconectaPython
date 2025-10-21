"""
URL configuration for icbfconecta project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # CRUD Madres
    path('madres/', views.listar_madres, name='listar_madres'),
    path('madres/crear/', views.crear_madre, name='crear_madre'),
    path('madres/editar/<int:id>/', views.editar_madre, name='editar_madre'),
    path('madres/eliminar/<int:id>/', views.eliminar_madre, name='eliminar_madre'),

    # core/urls.py
path('administradores/', views.listar_administradores, name='listar_administradores'),
path('administradores/crear/', views.crear_administrador, name='crear_administrador'),
path('administradores/editar/<int:id>/', views.editar_administrador, name='editar_administrador'),
path('administradores/eliminar/<int:id>/', views.eliminar_administrador, name='eliminar_administrador'),


]
