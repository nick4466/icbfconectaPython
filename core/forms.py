# core/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthForm(AuthenticationForm):
    # Definir el campo extra que agregaste en el HTML
    tipo_documento = forms.CharField(
        label='Tipo de Documento', 
        widget=forms.Select(choices=[
            ('', 'Seleccione...'),
            ('CC', 'Cédula de Ciudadanía (CC)'),
            ('TI', 'Tarjeta de Identidad (TI)'),
            ('RC', 'Registro Civil (RC)'),
            # Coincidir con las opciones de tu HTML
        ])
    )

    # El campo 'username' es el Número de Documento en tu lógica.
    # Podemos redefinir la etiqueta si es necesario.
    username = forms.CharField(label='Número de Documento', max_length=254)