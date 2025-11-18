from django.contrib import admin

from .models import Rol, Usuario, Padre, HogarComunitario, Nino, Asistencia, Planeacion

admin.site.register(Rol)
admin.site.register(Usuario)
admin.site.register(Padre)
admin.site.register(HogarComunitario)
admin.site.register(Nino)
admin.site.register(Asistencia)
admin.site.register(Planeacion)