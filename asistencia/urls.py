from django.urls import path
from . import views

urlpatterns = [
    path('', views.asistencia_form, name='asistencia_form'),
    path('historial/<int:nino_id>/', views.historial_asistencia, name='historial_asistencia'),
]
