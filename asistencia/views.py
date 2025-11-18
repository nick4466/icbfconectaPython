from django.shortcuts import render, redirect, get_object_or_404
from core.models import Nino, Asistencia
from datetime import date
from novedades.models import Novedad
from django.http import JsonResponse


from django.shortcuts import render, redirect, get_object_or_404
from core.models import Nino, Asistencia
from datetime import date
from django.http import JsonResponse

def asistencia_form(request):
    ninos = Nino.objects.all()

    if request.method == 'POST':
        # ✅ Leer la fecha desde el formulario
        fecha_str = request.POST.get('fecha')
        fecha_hoy = date.fromisoformat(fecha_str) if fecha_str else date.today()

        for nino in ninos:
            estado = request.POST.get(f'nino_{nino.id}')
            if estado:
                # ✅ Evita duplicados: actualiza si existe, crea si no
                Asistencia.objects.update_or_create(
                    nino=nino,
                    fecha=fecha_hoy,
                    defaults={'estado': estado}
                )

        return render(request, 'asistencia/asistencia_form.html', {
            'ninos': ninos,
            'fecha_hoy': fecha_hoy,
            'mensaje': 'Asistencia registrada exitosamente ✅'
        })

    # Si es GET, usar fecha de hoy por defecto
    fecha_hoy = date.today()
    return render(request, 'asistencia/asistencia_form.html', {
        'ninos': ninos,
        'fecha_hoy': fecha_hoy
    })


def historial_asistencia(request, nino_id):
    nino = get_object_or_404(Nino, id=nino_id)
    historial = Asistencia.objects.filter(nino=nino).order_by('-fecha')

    total = historial.count()
    presentes = historial.filter(estado="Presente").count()
    ausentes = historial.filter(estado="Ausente").count()
    justificados = historial.filter(estado="Justificado").count()

    def porcentaje(valor):
        return round((valor / total) * 100) if total > 0 else 0

    return render(request, 'asistencia/historial.html', {
        'nino': nino,
        'historial': historial,
        'presentes': presentes,
        'ausentes': ausentes,
        'justificados': justificados,
        'porc_presentes': porcentaje(presentes),
        'porc_ausentes': porcentaje(ausentes),
        'porc_justificados': porcentaje(justificados),
    })






def crear_novedad_desde_asistencia(request):
    if request.method == 'POST':
        nino_id = request.POST.get('nino_id')
        fecha = request.POST.get('fecha')
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')
        observaciones = request.POST.get('observaciones')

        # Crear novedad
        Novedad.objects.create(
            nino_id=nino_id,
            fecha=fecha,
            tipo=tipo,
            descripcion=descripcion,
            observaciones=observaciones
        )

        # Justificar asistencia: actualizar si existe, crear si no
        updated = Asistencia.objects.filter(nino_id=nino_id, fecha=fecha).update(estado="Justificado")
        if not updated:
            Asistencia.objects.create(nino_id=nino_id, fecha=fecha, estado="Justificado")

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})
