from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_planeaciones, name='lista_planeaciones'),
    path('registrar/', views.registrar_planeacion, name='registrar_planeacion'),
    path('editar/<int:id>/', views.editar_planeacion, name='editar_planeacion'),
    path('eliminar/<int:id>/', views.eliminar_planeacion, name='eliminar_planeacion'),
    path('detalle/<int:id>/', views.detalle_planeacion, name='detalle_planeacion'),
]
