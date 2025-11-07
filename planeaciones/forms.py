from django import forms
from .models import Planeacion

class PlaneacionForm(forms.ModelForm):
    class Meta:
        model = Planeacion
        exclude = ['madre']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'intencionalidad_pedagogica': forms.Textarea(attrs={'rows': 2}),
            'materiales_utilizar': forms.Textarea(attrs={'rows': 2}),
            'ambiente_educativo': forms.Textarea(attrs={'rows': 2}),
            'experiencia_inicio': forms.Textarea(attrs={'rows': 3}),
            'experiencia_pedagogica': forms.Textarea(attrs={'rows': 3}),
            'cierre_experiencia': forms.Textarea(attrs={'rows': 3}),
            'situaciones_presentadas': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'nombre_experiencia': 'Nombre de la experiencia',
            'intencionalidad_pedagogica': 'Intencionalidad pedagógica',
            'materiales_utilizar': 'Materiales a utilizar',
            'ambiente_educativo': 'Ambiente educativo',
            'experiencia_inicio': 'Inicio de la experiencia',
            'experiencia_pedagogica': 'Desarrollo de la experiencia pedagógica',
            'cierre_experiencia': 'Cierre de la experiencia',
            'situaciones_presentadas': 'Situaciones presentadas para el seguimiento de los niños y niñas',
        }   