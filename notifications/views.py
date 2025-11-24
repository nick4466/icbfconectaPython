from django.shortcuts import render
# Create your views here.
from django.http import JsonResponse
from .models import Notification

def marcar_todo_leido(request):
    if request.method == "POST":
        Notification.objects.filter(read=False).update(read=True)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})
