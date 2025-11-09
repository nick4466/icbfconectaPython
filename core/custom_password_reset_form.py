from django import forms
from django.contrib.auth.forms import PasswordResetForm
from core.models import Usuario

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Correo electrónico", max_length=254)

    def get_users(self, email):
        active_users = Usuario._default_manager.filter(email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def clean(self):
        email = self.cleaned_data.get("email")
        if not Usuario.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("No existe un usuario activo con ese correo.")
        return self.cleaned_data
