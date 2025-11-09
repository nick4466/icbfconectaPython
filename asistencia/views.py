from django.shortcuts import render, redirect, get_object_or_404
from core.models import Nino, Asistencia
from datetime import date

def asistencia_form(request):
    ninos = Nino.objects.all()
    fecha_hoy = date.today()

    if request.method == 'POST':
        for nino in ninos:
            estado = request.POST.get(f'nino_{nino.id}')
            if estado:
                Asistencia.objects.create(
                    nino=nino,
                    fecha=fecha_hoy,
                    estado=estado
                )
        return render(request, 'asistencia/asistencia_form.html', {
            'ninos': ninos,
            'fecha_hoy': fecha_hoy,
            'mensaje': 'Asistencia registrada exitosamente ✅'
        })

    return render(request, 'asistencia/asistencia_form.html', {
        'ninos': ninos,
        'fecha_hoy': fecha_hoy
    })

def historial_asistencia(request, nino_id):
    nino = get_object_or_404(Nino, id=nino_id)
    historial = Asistencia.objects.filter(nino=nino).order_by('-fecha')
    return render(request, 'asistencia/historial.html', {
        'nino': nino,
        'historial': historial
    })

    

