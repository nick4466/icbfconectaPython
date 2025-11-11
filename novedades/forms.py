from django import forms
from .models import Novedad

class NovedadForm(forms.ModelForm):
    class Meta:
        model = Novedad
        fields = ['nino', 'fecha', 'tipo', 'descripcion', 'docente', 'observaciones']
        widgets = {
            'tipo': forms.Select, 
        }
