from django import forms
from .models import Novedad
from core.models import Nino
from planeaciones.models import Planeacion
from .models import Novedad, Nino

class NovedadForm(forms.ModelForm):
    nino = forms.ModelChoiceField(queryset=Nino.objects.none())
    planeacion = forms.ModelChoiceField(
        queryset=Planeacion.objects.all(),
        required=False,
        label="Selecciona una Planeación",
        empty_label="-- Ninguna --"
    )

    class Meta:
        model = Novedad
        exclude = ['docente']
        fields = [
            'nino',
            'fecha',
            'tipo',
            'docente',
            'descripcion',
            'causa',
            'disposicion',
            'acuerdos',
            'observaciones',
            'archivo_pdf',
            'planeacion',  # reemplaza clase
        ]
        widgets = {
            'tipo': forms.Select(),
            'fecha': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'  # <--- importante para que se muestre la fecha existente
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Esto asegura que la fecha del instance se muestre correctamente
        if self.instance and self.instance.pk:
            self.fields['fecha'].initial = self.instance.fecha.strftime('%Y-%m-%d')
