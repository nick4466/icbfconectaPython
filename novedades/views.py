from django.shortcuts import render, get_object_or_404, redirect
from .models import Novedad
from .forms import NovedadForm

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


