from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Planeacion
from .forms import PlaneacionForm

@login_required
def lista_planeaciones(request):
    madre = request.user
    mes = request.GET.get('mes')  # filtro por mes

    if mes:
        planeaciones = Planeacion.objects.filter(madre=madre, fecha__month=mes).order_by('-fecha')
    else:
        planeaciones = Planeacion.objects.filter(madre=madre).order_by('-fecha')

    # Lista de meses para la barra de búsqueda
    meses = [
        ('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
        ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'),
        ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
    ]

    context = {
        'planeaciones': planeaciones,
        'mes_seleccionado': mes or '',
        'meses': meses,
    }

    return render(request, 'planeaciones/lista_planeaciones.html', context)


@login_required
def registrar_planeacion(request):
    if request.method == 'POST':
        form = PlaneacionForm(request.POST)
        if form.is_valid():
            planeacion = form.save(commit=False)
            planeacion.madre = request.user
            planeacion.save()
            return redirect('planeaciones:lista_planeaciones')
    else:
        form = PlaneacionForm()
    return render(request, 'planeaciones/registrar_planeacion.html', {'form': form})


@login_required
def editar_planeacion(request, id):
    planeacion = get_object_or_404(Planeacion, id=id, madre=request.user)
    if request.method == 'POST':
        form = PlaneacionForm(request.POST, instance=planeacion)
        if form.is_valid():
            form.save()
            return redirect('planeaciones:lista_planeaciones')
    else:
        form = PlaneacionForm(instance=planeacion)
    return render(request, 'planeaciones/editar_planeacion.html', {'form': form})


@login_required
def eliminar_planeacion(request, id):
    planeacion = get_object_or_404(Planeacion, id=id, madre=request.user)
    if request.method == 'POST':
        planeacion.delete()
        return redirect('planeaciones:lista_planeaciones')
    return render(request, 'planeaciones/eliminar_planeacion.html', {'planeacion': planeacion})


@login_required
def detalle_planeacion(request, id):
    planeacion = get_object_or_404(Planeacion, id=id, madre=request.user)
    return render(request, 'planeaciones/detalle_planeacion.html', {'planeacion': planeacion})
