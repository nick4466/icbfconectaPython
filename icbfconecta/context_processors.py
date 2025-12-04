def user_context(request):
    """
    Añade información del usuario al contexto de todos los templates.
    """
    context = {}
    # Asegurarnos de que el usuario está autenticado para evitar errores
    if request.user.is_authenticated:
        # Construimos el nombre completo. Ajusta 'nombres' y 'apellidos'
        # si los campos en tu modelo de Usuario se llaman diferente.
        nombre_completo = f"{request.user.nombres} {request.user.apellidos}".strip()

        # Añadimos el nombre y la foto de perfil al contexto
        context['nombre_madre'] = nombre_completo

        # 💡 CORRECCIÓN: Añadir la URL de la foto de perfil correcta para la madre.
        # La foto está en el perfil de la madre (madre_profile), no directamente en el usuario.
        if hasattr(request.user, 'madre_profile') and request.user.madre_profile.foto_madre:
            context['foto_perfil_url'] = request.user.madre_profile.foto_madre.url
        
        # Agregar notificaciones no leídas
        try:
            from notifications.models import Notification
            notifications = Notification.objects.filter(
                recipient=request.user,
                read=False
            ).order_by('-created_at')[:10]  # Limitar a las 10 más recientes
            
            context['notifications'] = notifications
            context['notifications_count'] = notifications.count()
        except Exception as e:
            print(f"Error al cargar notificaciones: {e}")
            context['notifications'] = []
            context['notifications_count'] = 0

    return context
