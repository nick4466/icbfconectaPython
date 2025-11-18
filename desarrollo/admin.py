from django.contrib import admin
from .models import DesarrolloNino

@admin.register(DesarrolloNino)
class DesarrolloNinoAdmin(admin.ModelAdmin):
    list_display = ('nino', 'fecha_fin_mes')
    list_filter = ('fecha_fin_mes', 'nino__hogar')
    search_fields = ('nino__nombres', 'nino__apellidos')

