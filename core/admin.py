from django.contrib import admin

from .models import Rol, Usuario, Padre, HogarComunitario, Nino, Asistencia, Planeacion, Regional, Ciudad, HistorialCambio

# Registrar modelos adicionales para poder administrar regionales y ciudades desde el admin
admin.site.register(Rol)
admin.site.register(Usuario)
admin.site.register(Padre)
admin.site.register(HogarComunitario)
admin.site.register(Nino)
admin.site.register(Asistencia)
admin.site.register(Planeacion)
admin.site.register(Regional)
admin.site.register(Ciudad)

@admin.register(HistorialCambio)
class HistorialCambioAdmin(admin.ModelAdmin):
    list_display = ('tipo_modelo', 'objeto_id', 'campo_modificado', 'accion', 'usuario', 'fecha_cambio')
    list_filter = ('tipo_modelo', 'accion', 'fecha_cambio')
    search_fields = ('campo_modificado', 'observaciones', 'objeto_id')
    readonly_fields = ('tipo_modelo', 'objeto_id', 'campo_modificado', 'valor_anterior', 'valor_nuevo', 'accion', 'usuario', 'fecha_cambio', 'observaciones')
    ordering = ('-fecha_cambio',)