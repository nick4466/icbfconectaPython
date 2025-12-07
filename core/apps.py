from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        import core.signals
        
        # Iniciar tareas programadas solo en el proceso principal
        # Evita duplicación en workers de desarrollo
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return
        
        try:
            from core.scheduler import iniciar_tareas_programadas
            iniciar_tareas_programadas()
        except Exception as e:
            print(f"Error al iniciar tareas programadas: {e}")