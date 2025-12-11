"""
Decoradores personalizados para control de acceso basado en roles
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def rol_requerido(nombre_rol):
    """Decorador que verifica si el usuario tiene un rol específico."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Asegurarse de que el usuario esté autenticado y tenga el rol correcto
            if not request.user.is_authenticated or not hasattr(request.user, 'rol') or request.user.rol.nombre_rol != nombre_rol:
                messages.error(request, 'Acceso denegado. No tienes los permisos necesarios.')
                return redirect('home')  # Redirigir a una página de inicio o de error
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
