from django.shortcuts import render, get_object_or_404, redirect
from .models import Novedad
from .forms import NovedadForm
from django.db.models import Q
from datetime import datetime
from core.models import Nino, Asistencia
from django.contrib import messages

def novedades_list(request):
    query = request.GET.get('q')
    novedades = Novedad.objects.select_related('nino').all().order_by('-fecha')

    if query:
        filtros = (
            Q(nino__nombres__icontains=query) |
            Q(nino__apellidos__icontains=query) |
            Q(tipo__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(clase__icontains=query)
        )
        try:
            fecha_busqueda = datetime.strptime(query, "%d/%m/%Y").date()
            filtros |= Q(fecha=fecha_busqueda)
        except ValueError:
            pass

        novedades = novedades.filter(filtros)

    return render(request, 'novedades/list.html', {'novedades': novedades, 'query': query})


def novedades_create(request):
    form = NovedadForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('novedades_list')
    return render(request, 'novedades/create.html', {'form': form})


def novedades_edit(request, pk):
    novedad = get_object_or_404(Novedad, pk=pk)
    form = NovedadForm(request.POST or None, instance=novedad)
    if form.is_valid():
        form.save()
        return redirect('novedades_list')
    return render(request, 'novedades/form.html', {'form': form})


def novedades_delete(request, pk):
    novedad = get_object_or_404(Novedad, pk=pk)
    if request.method == 'POST':
        novedad.delete()
        return redirect('novedades_list')
    return render(request, 'novedades/confirm_delete.html', {'novedad': novedad})


def novedades_detail(request, pk):
    novedad = get_object_or_404(Novedad, pk=pk)
    return render(request, 'novedades/detail.html', {'novedad': novedad})


def justificar_ausencia(request, novedad_id):
    novedad = get_object_or_404(Novedad, id=novedad_id)
    novedad.ausencia_justificada = True
    novedad.save()
    # Mantener coherencia: actualizar asistencia también
    Asistencia.objects.filter(nino=novedad.nino, fecha=novedad.fecha).update(estado="Justificado")
    return redirect('novedades_list')


def nueva_novedad(request):
    nino_id = request.GET.get('nino_id')
    fecha = request.GET.get('fecha')

    initial = {}
    nino = None
    if nino_id:
        nino = get_object_or_404(Nino, id=nino_id)
        initial['nino'] = nino

    if request.method == 'POST':
        form = NovedadForm(request.POST)
        if form.is_valid():
            novedad = form.save()
            if nino_id and fecha:
                # Justificar todas las asistencias de ese niño en esa fecha
                updated = Asistencia.objects.filter(nino_id=nino_id, fecha=fecha).update(estado="Justificado")
                if not updated:
                    Asistencia.objects.create(nino_id=nino_id, fecha=fecha, estado="Justificado")
                messages.success(request, "Novedad registrada y ausencia justificada.")
            return redirect('novedades_list')
    else:
        form = NovedadForm(initial=initial)

    return render(request, 'novedades/nueva.html', {'form': form, 'nino': nino, 'fecha': fecha})



def detalle_novedad(request, novedad_id):
    novedad = get_object_or_404(Novedad, id=novedad_id)
    return render(request, 'novedades/detalle.html', {'novedad': novedad})

