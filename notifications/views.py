from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from django.http import JsonResponse
from .models import Notification
from django.contrib.auth.decorators import login_required

@login_required
def marcar_todo_leido(request):
    if request.method == "POST":
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
def marcar_leida(request, notification_id):
    """Marca una notificación específica como leída"""
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.read = True
        notification.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
def ver_notificacion(request, notification_id):
    """
    Marca la notificación como leída y redirige al objeto relacionado.
    Para solicitudes de matrícula, redirige al panel de revisión.
    """
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    
    # Marcar como leída
    notification.read = True
    notification.save()
    
    # Determinar a dónde redirigir según el tipo de objeto
    if notification.content_type:
        model_name = notification.content_type.model
        
        if model_name == 'solicitudmatriculacion':
            # Redirigir al panel de revisión de solicitudes
            return redirect('panel_revision_solicitudes')
        elif model_name == 'novedad':
            # Redirigir a detalle de novedad
            return redirect('novedades:detalle_madre', pk=notification.object_id)
        else:
            # Por defecto, redirigir a la lista de notificaciones
            return redirect('notifications:list')
    
    # Si no tiene objeto relacionado, ir a lista de notificaciones
    return redirect('notifications:list')


@login_required
def notificaciones_list(request):
    # Filtrar solo las notificaciones del usuario logueado
    notificaciones = Notification.objects.filter(recipient=request.user).order_by('-created_at')

    return render(request, 'notificaciones/list.html', {
        'notificaciones': notificaciones
    })
