from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('marcar-todo-leido/', views.marcar_todo_leido, name='marcar_todo_leido'),
    path('<int:notification_id>/mark-read/', views.marcar_leida, name='marcar_leida'),
    path('', views.notificaciones_list, name='list'),
]
