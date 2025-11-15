from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from core.models import Nino, HogarComunitario, Padre
from .models import DesarrolloNino

# -----------------------------------------------------------------
# VISTA DEL PADRE
# -----------------------------------------------------------------
@login_required
def padre_ver_desarrollo(request, nino_id):
    if request.user.rol.nombre_rol != 'padre':
        return redirect('role_redirect')

    try:
        padre = Padre.objects.get(usuario=request.user)
        # Obtener el niño específico y verificar que pertenece al padre
        nino = get_object_or_404(Nino, id=nino_id, padre=padre)
        
        desarrollos = []
        if nino:
            desarrollos = DesarrolloNino.objects.filter(nino=nino).order_by('-fecha_fin_mes')

        return render(request, 'padre/desarrollo_list.html', {'nino': nino, 'desarrollos': desarrollos})
    except (Padre.DoesNotExist, Nino.DoesNotExist):
        return redirect('padre_dashboard')

# -----------------------------------------------------------------
# CRUD DESARROLLO PARA MADRE COMUNITARIA
# -----------------------------------------------------------------
@login_required
def registrar_desarrollo(request):
    # Esta vista ahora solo maneja la creación
    nino_id_preseleccionado = request.GET.get('nino')

    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    try:
        hogar_madre = HogarComunitario.objects.get(madre=request.user.madre_profile)
    except HogarComunitario.DoesNotExist:
        return redirect('madre_dashboard')

    ninos_del_hogar = Nino.objects.filter(hogar=hogar_madre)

    # Mapeo de ratings a descripciones para autocompletado
    rating_map = {
        "1": "Malo",
        "2": "Regular",
        "3": "Bueno",
        "4": "Muy Bueno",
        "5": "Excelente",
    }

    if request.method == 'POST':
        nino_id = request.POST.get('nino')
        fecha_registro = request.POST.get('fecha_registro')

        # --- Capturar ratings y observaciones ---
        rating_cognitiva = request.POST.get('rating_cognitiva')
        cognitiva_obs = request.POST.get('dimension_cognitiva', '').strip()
        cognitiva = cognitiva_obs if cognitiva_obs else rating_map.get(rating_cognitiva, "")

        rating_comunicativa = request.POST.get('rating_comunicativa')
        comunicativa_obs = request.POST.get('dimension_comunicativa', '').strip()
        comunicativa = comunicativa_obs if comunicativa_obs else rating_map.get(rating_comunicativa, "")

        rating_socio_afectiva = request.POST.get('rating_socio_afectiva')
        socio_afectiva_obs = request.POST.get('dimension_socio_afectiva', '').strip()
        socio_afectiva = socio_afectiva_obs if socio_afectiva_obs else rating_map.get(rating_socio_afectiva, "")

        rating_corporal = request.POST.get('rating_corporal')
        corporal_obs = request.POST.get('dimension_corporal', '').strip()
        corporal = corporal_obs if corporal_obs else rating_map.get(rating_corporal, "")
        
        # --- Validación de campos obligatorios con mensajes de error específicos ---
        errores = []
        if not nino_id:
            errores.append("debes seleccionar un niño")
        if not fecha_registro:
            errores.append("debes seleccionar una fecha")
        if not rating_cognitiva:
            errores.append("debes calificar la dimensión cognitiva")
        if not rating_comunicativa:
            errores.append("debes calificar la dimensión comunicativa")
        if not rating_socio_afectiva:
            errores.append("debes calificar la dimensión socio-afectiva")
        if not rating_corporal:
            errores.append("debes calificar la dimensión corporal")

        if errores:
            mensaje_error = "Error: " + ", ".join(errores) + "."
            return render(request, 'madre/desarrollo_form.html', {
                'ninos': ninos_del_hogar,
                'nino_id_preseleccionado': nino_id,
                'error': mensaje_error.capitalize()
            })

        DesarrolloNino.objects.create(
            nino_id=nino_id,
            fecha_fin_mes=fecha_registro,
            rating_cognitiva=rating_cognitiva,
            rating_comunicativa=rating_comunicativa,
            rating_socio_afectiva=rating_socio_afectiva,
            rating_corporal=rating_corporal,
            dimension_cognitiva=cognitiva,
            dimension_comunicativa=comunicativa,
            dimension_socio_afectiva=socio_afectiva,
            dimension_corporal=corporal,
        )
        
        redirect_url = reverse('desarrollo:listar_desarrollos')
        return redirect(f'{redirect_url}?nino={nino_id}&exito=1')

    return render(request, 'madre/desarrollo_form.html', {
        'ninos': ninos_del_hogar,
        'form_action': reverse('desarrollo:registrar_desarrollo'),
        'titulo_form': 'Registrar Desarrollo de Niño',
        'nino_id_preseleccionado': nino_id_preseleccionado,
    })

@login_required
def listar_desarrollos(request):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')
    
    try:
        hogar_madre = HogarComunitario.objects.get(madre=request.user.madre_profile)
    except HogarComunitario.DoesNotExist:
        return render(request, 'madre/desarrollo_list.html', {'error': 'No tienes un hogar asignado.'})

    desarrollos = DesarrolloNino.objects.filter(nino__hogar=hogar_madre).select_related('nino', 'nino__padre__usuario').order_by('-fecha_fin_mes')
    ninos_del_hogar = Nino.objects.filter(hogar=hogar_madre)

    nino_id_filtro = request.GET.get('nino')
    if nino_id_filtro:
        desarrollos = desarrollos.filter(nino__id=nino_id_filtro)

    return render(request, 'madre/desarrollo_list.html', {
        'desarrollos': desarrollos,
        'ninos': ninos_del_hogar,
        'nino_id_filtro': nino_id_filtro,
    })

@login_required
def editar_desarrollo(request, id):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    desarrollo = get_object_or_404(DesarrolloNino, id=id)

    # Verificación de seguridad: la madre solo puede editar registros de su hogar.
    if desarrollo.nino.hogar.madre != request.user.madre_profile:
        return redirect('desarrollo:listar_desarrollos')

    # Mapeo de ratings a descripciones
    rating_map = {
        "1": "Malo",
        "2": "Regular",
        "3": "Bueno",
        "4": "Muy Bueno",
        "5": "Excelente",
    }

    if request.method == 'POST':
        desarrollo.fecha_fin_mes = request.POST.get('fecha_registro')

        # --- Actualizar ratings y dimensiones ---
        desarrollo.rating_cognitiva = request.POST.get('rating_cognitiva')
        cognitiva_obs = request.POST.get('dimension_cognitiva', '').strip()
        desarrollo.dimension_cognitiva = cognitiva_obs if cognitiva_obs else rating_map.get(desarrollo.rating_cognitiva, "")

        desarrollo.rating_comunicativa = request.POST.get('rating_comunicativa')
        comunicativa_obs = request.POST.get('dimension_comunicativa', '').strip()
        desarrollo.dimension_comunicativa = comunicativa_obs if comunicativa_obs else rating_map.get(desarrollo.rating_comunicativa, "")

        desarrollo.rating_socio_afectiva = request.POST.get('rating_socio_afectiva')
        socio_afectiva_obs = request.POST.get('dimension_socio_afectiva', '').strip()
        desarrollo.dimension_socio_afectiva = socio_afectiva_obs if socio_afectiva_obs else rating_map.get(desarrollo.rating_socio_afectiva, "")

        desarrollo.rating_corporal = request.POST.get('rating_corporal')
        corporal_obs = request.POST.get('dimension_corporal', '').strip()
        desarrollo.dimension_corporal = corporal_obs if corporal_obs else rating_map.get(desarrollo.rating_corporal, "")

        desarrollo.save()

        redirect_url = reverse('desarrollo:listar_desarrollos')
        return redirect(f'{redirect_url}?nino={desarrollo.nino.id}&exito=1')

    return render(request, 'madre/desarrollo_form.html', {
        'desarrollo': desarrollo,
        'form_action': reverse('desarrollo:editar_desarrollo', args=[id]),
        'titulo_form': 'Editar Registro de Desarrollo',
        'nino_id_preseleccionado': desarrollo.nino.id,
    })

@login_required
def eliminar_desarrollo(request, id):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    desarrollo = get_object_or_404(DesarrolloNino, id=id)

    if desarrollo.nino.hogar.madre != request.user.madre_profile:
        return redirect('desarrollo:listar_desarrollos')

    nino_id = desarrollo.nino.id
    desarrollo.delete()
    
    return redirect(reverse('desarrollo:listar_desarrollos') + f'?nino={nino_id}')
