from django import forms
from .models import Novedad

class NovedadForm(forms.ModelForm):
    class Meta:
        model = Novedad
        exclude = ['docente']
        fields = [
            'nino',
            'fecha',
            'clase',
            'tipo',
            'docente',
            'descripcion',
            'causa',
            'disposicion',
            'acuerdos',
            'observaciones',
        ]
        widgets = {
            'tipo': forms.Select(),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

