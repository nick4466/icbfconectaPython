from django.shortcuts import render, get_object_or_404, redirect
from .models import Novedad
from .forms import NovedadForm
from django.db.models import Q
from datetime import datetime


def novedades_list(request):
    novedades = Novedad.objects.all().order_by('-fecha')
    return render(request, 'novedades/list.html', {'novedades': novedades})

def novedades_create(request):
    form = NovedadForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('novedades_list')
    return render(request, 'novedades/form.html', {'form': form})

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

def novedades_create(request):
    form = NovedadForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('novedades_list')
    return render(request, 'novedades/create.html', {'form': form})


def novedades_list(request):
    query = request.GET.get('q')
    novedades = Novedad.objects.select_related('nino').all()

    if query:
        filtros = Q(nino__nombres__icontains=query) | Q(nino__apellidos__icontains=query) | Q(tipo__icontains=query) | Q(descripcion__icontains=query) | Q(clase__icontains=query)

        # Intentar convertir la búsqueda a fecha
        try:
            fecha_busqueda = datetime.strptime(query, "%d/%m/%Y").date()
            filtros |= Q(fecha=fecha_busqueda)
        except ValueError:
            pass  # No es una fecha válida, ignoramos

        novedades = novedades.filter(filtros)

    return render(request, 'novedades/list.html', {'novedades': novedades, 'query': query})



from django.shortcuts import get_object_or_404, redirect

def justificar_ausencia(request, novedad_id):
    novedad = get_object_or_404(Novedad, id=novedad_id)
    novedad.ausencia_justificada = True
    novedad.save()
    return redirect('novedades_list')  # Ajusta al nombre de tu vista/listado

