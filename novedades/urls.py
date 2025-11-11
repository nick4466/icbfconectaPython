from django.urls import path
from .views import novedades_list, novedades_create, novedades_edit, novedades_delete, novedades_detail

urlpatterns = [
    path('', novedades_list, name='novedades_list'),
    path('nueva/', novedades_create, name='novedades_create'),
    path('editar/<int:pk>/', novedades_edit, name='novedades_edit'),
    path('eliminar/<int:pk>/', novedades_delete, name='novedades_delete'),
    path('detalle/<int:pk>/', novedades_detail, name='novedades_detail'),

]
