from django import forms
from .models import Planeacion, Documentacion

# Form para Planeacion
class PlaneacionForm(forms.ModelForm):
    class Meta:
        model = Planeacion
        exclude = ['madre']  # El usuario se asigna en la vista
        widgets = {
            'fecha': forms.DateInput(
                attrs={
                    'type': 'date',
                    'placeholder': 'Seleccione la fecha'
                }
            ),
            'nombre_experiencia': forms.TextInput(
                attrs={
                    'placeholder': 'Nombre de la Planeación Pedagógica'
                }
            ),
            'intencionalidad_pedagogica': forms.Textarea(
                attrs={
                    'rows': 2,
                    'placeholder': 'Describe el proposito de la planeación pedagógica'
                }
            ),
            'materiales_utilizar': forms.Textarea(
                attrs={
                    'rows': 2,
                    'placeholder': 'Materiales necesarios para las actividades'
                }
            ),
            'ambiente_educativo': forms.Textarea(
                attrs={
                    'rows': 2,
                    'placeholder': 'Cómo vas a ambientar el aula o espacio educativo?'
                }
            ),
            'experiencia_inicio': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Describe el inicio de la experiencia'
                }
            ),
            'experiencia_pedagogica': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Describe el desarrollo de la experiencia pedagógica'
                }
            ),
            'cierre_experiencia': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Cómo finaliza la actividad?'
                }
            ),
            'situaciones_presentadas': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Observaciones y situaciones presentadas'
                }
            ),
        }
        labels = {
            'nombre_experiencia': 'Nombre de la experiencia',
            'intencionalidad_pedagogica': 'Intencionalidad pedagógica',
            'materiales_utilizar': 'Materiales a utilizar',
            'ambiente_educativo': 'Como vas a decorar el aula o el espacio educativo?',
            'experiencia_inicio': 'Inicio de la experiencia',
            'experiencia_pedagogica': 'Desarrollo de la experiencia pedagógica',
            'cierre_experiencia': 'Cierre de la experiencia',
            'situaciones_presentadas': 'Situaciones presentadas para el seguimiento de los niños y niñas',
        }

# Form para Documentacion
class DocumentacionForm(forms.ModelForm):
    class Meta:
        model = Documentacion
        fields = ['imagen']
