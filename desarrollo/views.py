from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from .models import DesarrolloNino
from novedades.models import Novedad
from core.models import Nino, HogarComunitario, Padre, MadreComunitaria
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
import os
from django.core.paginator import Paginator
from django.templatetags.static import static


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
    
    nino_id_preseleccionado = request.GET.get('nino')

    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    try:
        hogar_madre = HogarComunitario.objects.get(madre__usuario=request.user)
    except HogarComunitario.DoesNotExist:
        return redirect('madre_dashboard')

    ninos_del_hogar = Nino.objects.filter(hogar=hogar_madre)

    # Mapeo de ratings a descripciones
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

        # ----- VALIDACIÓN DE CAMPOS OBLIGATORIOS -----
        errores = []

        if not nino_id:
            errores.append("debes seleccionar un niño")

        if not fecha_registro:
            errores.append("debes seleccionar una fecha")

        if not request.POST.get('rating_cognitiva'):
            errores.append("debes calificar la dimensión cognitiva")

        if not request.POST.get('rating_comunicativa'):
            errores.append("debes calificar la dimensión comunicativa")

        if not request.POST.get('rating_socio_afectiva'):
            errores.append("debes calificar la dimensión socio-afectiva")

        if not request.POST.get('rating_corporal'):
            errores.append("debes calificar la dimensión corporal")

        # Si faltan datos → enviar mensaje de error
        if errores:
            mensaje_error = "Error: " + ", ".join(errores) + "."
            return render(request, 'madre/desarrollo_form.html', {
                'ninos': ninos_del_hogar,
                'nino_id_preseleccionado': nino_id,
                'error': mensaje_error.capitalize(),
            })

        # ----- VALIDAR REGISTRO DUPLICADO -----
        if DesarrolloNino.objects.filter(
            nino_id=nino_id,
            fecha_fin_mes=fecha_registro
        ).exists():
            return render(request, 'madre/desarrollo_form.html', {
                'ninos': ninos_del_hogar,
                'nino_id_preseleccionado': nino_id,
                'error': "Ya existe un registro para este niño en esa fecha.",
            })

        # ----- OBTENER CALIFICACIONES Y GENERAR DESCRIPCIÓN -----
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

        # ----- CREACIÓN DEL REGISTRO -----
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

    # ----- CARGA INICIAL DEL FORMULARIO -----
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
        hogar_madre = HogarComunitario.objects.get(madre__usuario=request.user)
    except HogarComunitario.DoesNotExist:
        return render(request, 'madre/desarrollo_list.html', {'error': 'No tienes un hogar asignado.'})

    desarrollos = DesarrolloNino.objects.filter(nino__hogar=hogar_madre).select_related('nino', 'nino__padre__usuario').order_by('-fecha_fin_mes')
    ninos_del_hogar = Nino.objects.filter(hogar=hogar_madre)

    # --- Lógica de Filtrado Mejorada ---
    nino_id_filtro = request.GET.get('nino', '')
    mes_filtro = request.GET.get('mes', '') # YYYY-MM

    if nino_id_filtro:
        desarrollos = desarrollos.filter(nino__id=nino_id_filtro)

    if mes_filtro:
        try:
            year, month = map(int, mes_filtro.split('-'))
            desarrollos = desarrollos.filter(fecha_fin_mes__year=year, fecha_fin_mes__month=month)
        except (ValueError, TypeError):
            pass

    # === LÓGICA DE DIFERENCIACIÓN DE CARDS ===
    hoy = timezone.now().date()
    desarrollos_list = []
    for desarrollo in desarrollos:
        # Calcular promedio
        ratings = [
            desarrollo.rating_cognitiva or 0,
            desarrollo.rating_comunicativa or 0,
            desarrollo.rating_socio_afectiva or 0,
            desarrollo.rating_corporal or 0,
        ]
        promedio = sum(ratings) / 4 if all(ratings) else 0
        desarrollo.promedio = round(promedio, 1)
        # Badge/accent/icon
        if promedio >= 4.5:
            desarrollo.badge = 'Excelente'
            desarrollo.accent = 'card-accent-excelente'
            desarrollo.icon = 'fa-baby'
        elif promedio >= 3.5:
            desarrollo.badge = 'Muy Bueno'
            desarrollo.accent = 'card-accent-muybueno'
            desarrollo.icon = 'fa-child'
        elif promedio >= 2.5:
            desarrollo.badge = 'Bueno'
            desarrollo.accent = 'card-accent-bueno'
            desarrollo.icon = 'fa-smile'
        elif promedio >= 1.5:
            desarrollo.badge = 'Regular'
            desarrollo.accent = 'card-accent-regular'
            desarrollo.icon = 'fa-meh'
        else:
            desarrollo.badge = 'Malo'
            desarrollo.accent = 'card-accent-malo'
            desarrollo.icon = 'fa-frown'
        # ¿Es del mes actual?
        if desarrollo.fecha_fin_mes.year == hoy.year and desarrollo.fecha_fin_mes.month == hoy.month:
            desarrollo.accent += ' card-accent-actual'
            desarrollo.is_actual = True
        else:
            desarrollo.is_actual = False
        desarrollos_list.append(desarrollo)

    # --- Paginación ---
    paginator = Paginator(desarrollos_list, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    filtros = {
        'nino': nino_id_filtro,
        'mes': mes_filtro,
    }

    return render(request, 'madre/desarrollo_list.html', {
        'desarrollos': page_obj,
        'ninos': ninos_del_hogar,
        'nino_id_filtro': nino_id_filtro,
        'mes_filtro': mes_filtro,
        'filtros': filtros,
    })

@login_required
def editar_desarrollo(request, id):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    desarrollo = get_object_or_404(DesarrolloNino, id=id)

    # Verificación de seguridad: la madre solo puede editar registros de su hogar.
    if desarrollo.nino.hogar.madre.usuario != request.user:
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

        nueva_fecha = request.POST.get('fecha_registro')

        # ----- VALIDACIONES OBLIGATORIAS -----
        errores = []
        if not nueva_fecha:
            errores.append("debes seleccionar una fecha")

        if not request.POST.get('rating_cognitiva'):
            errores.append("debes calificar la dimensión cognitiva")

        if not request.POST.get('rating_comunicativa'):
            errores.append("debes calificar la dimensión comunicativa")

        if not request.POST.get('rating_socio_afectiva'):
            errores.append("debes calificar la dimensión socio-afectiva")

        if not request.POST.get('rating_corporal'):
            errores.append("debes calificar la dimensión corporal")

        # Si faltan datos → regresar el error
        if errores:
            mensaje_error = "Error: " + ", ".join(errores) + "."
            return render(request, 'madre/desarrollo_form.html', {
                'desarrollo': desarrollo,
                'form_action': reverse('desarrollo:editar_desarrollo', args=[id]),
                'titulo_form': 'Editar Registro de Desarrollo',
                'nino_id_preseleccionado': desarrollo.nino.id,
                'error': mensaje_error.capitalize(),
            })

        # ----- VALIDAR DUPLICADO DE FECHA PARA ESTE NIÑO -----
        if DesarrolloNino.objects.filter(
            nino=desarrollo.nino,
            fecha_fin_mes=nueva_fecha
        ).exclude(id=desarrollo.id).exists():
            return render(request, 'madre/desarrollo_form.html', {
                'desarrollo': desarrollo,
                'form_action': reverse('desarrollo:editar_desarrollo', args=[id]),
                'titulo_form': 'Editar Registro de Desarrollo',
                'nino_id_preseleccionado': desarrollo.nino.id,
                'error': "Ya existe un registro para este niño en esa fecha.",
            })

        # ----- GUARDAR CAMBIOS -----
        desarrollo.fecha_fin_mes = nueva_fecha

        desarrollo.rating_cognitiva = request.POST.get('rating_cognitiva')
        cognitiva_obs = request.POST.get('dimension_cognitiva', '').strip()
        desarrollo.dimension_cognitiva = (
            cognitiva_obs if cognitiva_obs else rating_map.get(desarrollo.rating_cognitiva, "")
        )

        desarrollo.rating_comunicativa = request.POST.get('rating_comunicativa')
        comunicativa_obs = request.POST.get('dimension_comunicativa', '').strip()
        desarrollo.dimension_comunicativa = (
            comunicativa_obs if comunicativa_obs else rating_map.get(desarrollo.rating_comunicativa, "")
        )

        desarrollo.rating_socio_afectiva = request.POST.get('rating_socio_afectiva')
        socio_afectiva_obs = request.POST.get('dimension_socio_afectiva', '').strip()
        desarrollo.dimension_socio_afectiva = (
            socio_afectiva_obs if socio_afectiva_obs else rating_map.get(desarrollo.rating_socio_afectiva, "")
        )

        desarrollo.rating_corporal = request.POST.get('rating_corporal')
        corporal_obs = request.POST.get('dimension_corporal', '').strip()
        desarrollo.dimension_corporal = (
            corporal_obs if corporal_obs else rating_map.get(desarrollo.rating_corporal, "")
        )

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

    if desarrollo.nino.hogar.madre.usuario != request.user:
        return redirect('desarrollo:listar_desarrollos')

    nino_id = desarrollo.nino.id
    desarrollo.delete()
    
    return redirect(reverse('desarrollo:listar_desarrollos') + f'?nino={nino_id}')

@login_required
def generar_reporte(request):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    try:
        hogar_madre = HogarComunitario.objects.get(madre__usuario=request.user)
    except HogarComunitario.DoesNotExist:
        return render(request, 'madre/reporte_form.html', {'error': 'No tienes un hogar asignado.'})

    ninos_del_hogar = Nino.objects.filter(hogar=hogar_madre)
    context = {'ninos': ninos_del_hogar}

    if request.method == 'GET' and 'nino' in request.GET:
        nino_id = request.GET.get('nino')
        tipo_reporte = request.GET.get('tipo_reporte', 'ambos')
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        if nino_id:
            nino_seleccionado = get_object_or_404(Nino, id=nino_id, hogar=hogar_madre)
            desarrollos = []
            novedades = []

            # Filtrar Desarrollos
            if tipo_reporte in ['desarrollos', 'ambos']:
                query_desarrollo = DesarrolloNino.objects.filter(nino=nino_seleccionado)
                if fecha_inicio:
                    query_desarrollo = query_desarrollo.filter(fecha_fin_mes__gte=fecha_inicio)
                if fecha_fin:
                    query_desarrollo = query_desarrollo.filter(fecha_fin_mes__lte=fecha_fin)
                desarrollos = query_desarrollo.order_by('fecha_fin_mes')

            # Filtrar Novedades
            if tipo_reporte in ['novedades', 'ambos']:
                query_novedad = Novedad.objects.filter(nino=nino_seleccionado)
                if fecha_inicio:
                    query_novedad = query_novedad.filter(fecha__gte=fecha_inicio)
                if fecha_fin:
                    query_novedad = query_novedad.filter(fecha__lte=fecha_fin)
                novedades = query_novedad.order_by('fecha')

            context.update({
                'nino_seleccionado': nino_seleccionado,
                'desarrollos': desarrollos,
                'novedades': novedades,
                'filtros': request.GET, # Pasa los filtros para mantenerlos en el form
                'mostrar_resumen': True
            })

    return render(request, 'madre/reporte_form.html', context)

@login_required
def reporte_resumen(request, nino_id):
    nino = get_object_or_404(Nino, id=nino_id)
    
    # Asegurarse de que la madre solo pueda ver niños de su hogar
    if not request.user.is_staff:
        try:
            hogar_madre = HogarComunitario.objects.get(madre__usuario=request.user)
            if nino.hogar != hogar_madre:
                return redirect('gestion_ninos')
        except HogarComunitario.DoesNotExist:
            return redirect('gestion_ninos')

    desarrollos = DesarrolloNino.objects.filter(nino=nino).order_by('-fecha_fin_mes')
    novedades = Novedad.objects.filter(nino=nino).order_by('-fecha')

    context = {
        'nino': nino,
        'desarrollos': desarrollos,
        'novedades': novedades,
    }
    return render(request, 'reporte/reporte_resumen.html', context)


@login_required
def generar_reporte_pdf(request, nino_id):
    nino = get_object_or_404(Nino, id=nino_id)

    tipo_reporte = request.GET.get('tipo_reporte', 'ambos')

    # Obtener fechas como strings
    fecha_inicio_str = request.GET.get('fecha_inicio') or None
    fecha_fin_str = request.GET.get('fecha_fin') or None

    # Convertir fechas SOLO si vienen
    def parse_fecha(f):
        try:
            return datetime.strptime(f, '%Y-%m-%d').date() if f else None
        except:
            return None

    fecha_inicio = parse_fecha(fecha_inicio_str)
    fecha_fin = parse_fecha(fecha_fin_str)

    # Base de consultas vacías
    desarrollos = DesarrolloNino.objects.none()
    novedades = Novedad.objects.none()

    # Aplicar tipo de reporte
    if tipo_reporte in ['ambos', 'desarrollo']:
        desarrollos = DesarrolloNino.objects.filter(nino=nino)

    if tipo_reporte in ['ambos', 'novedades']:
        novedades = Novedad.objects.filter(nino=nino)

    # Aplicar filtros de fecha de forma SEGURA
    if fecha_inicio:
        desarrollos = desarrollos.filter(fecha_fin_mes__gte=fecha_inicio)
        novedades = novedades.filter(fecha__gte=fecha_inicio)

    if fecha_fin:
        desarrollos = desarrollos.filter(fecha_fin_mes__lte=fecha_fin)
        novedades = novedades.filter(fecha__lte=fecha_fin)
    
    logo_url = request.build_absolute_uri(static('img/logoSinFondo.png'))

    # Renderizar plantilla HTML
    template_path = 'reporte/reporte_pdf.html'
    context = {
        'nino': nino,
        'desarrollos': desarrollos.order_by('fecha_fin_mes'),
        'novedades': novedades.order_by('fecha'),
        'tipo_reporte': tipo_reporte,
        'fecha_inicio': fecha_inicio_str or "N/A",
        'fecha_fin': fecha_fin_str or "N/A",
        'logo_url': logo_url,
        'hogar_comunitario': nino.hogar, # Mover aquí
    }
    template = get_template(template_path)
    html = template.render(context)

    # Generar PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="reporte_{nino.nombres}_{nino.apellidos}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generando PDF. <pre>' + html + '</pre>')

    return response
