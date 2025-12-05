def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Esto asegura que la fecha del instance se muestre correctamente
    if self.instance and self.instance.pk:
        self.fields['fecha'].initial = self.instance.fecha.strftime('%Y-%m-%d')
    
    # Archivo opcional
    self.fields['archivo_pdf'].required = False


    # Filtrar NIÑOS por hogar
    if self.request:
        madre_profile = self.request.user.madre_profile
        hogar = madre_profile.hogarcomunitario_set.first()

        self.fields['nino'].queryset = Nino.objects.filter(hogar=hogar)

        # Filtrar planeaciones solo de la madre
        self.fields['planeacion'].queryset = Planeacion.objects.filter(madre=self.request.user)

    # Mostrar fecha existente correctamente
    if self.instance and self.instance.pk:
        self.fields['fecha'].initial = self.instance.fecha.strftime('%Y-%m-%d')
