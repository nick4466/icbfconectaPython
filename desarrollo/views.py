from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from .models import DesarrolloNino, SeguimientoDiario
from planeaciones.models import Planeacion as PlaneacionModel
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
import calendar


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
    nino_filtrado = None  # Inicializamos la variable

    if nino_id_filtro:
        desarrollos = desarrollos.filter(nino__id=nino_id_filtro)
        try:
            # Obtenemos el objeto del niño para pasarlo a la plantilla
            nino_filtrado = Nino.objects.get(id=nino_id_filtro, hogar=hogar_madre)
        except Nino.DoesNotExist:
            # Si el niño no existe o no pertenece al hogar, no hacemos nada
            pass

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
        promedio = desarrollo.valoracion_promedio_mes or 0

        # Badge/accent/icon
        if promedio >= 4.0:
            desarrollo.badge = 'Excelente'
            desarrollo.accent = 'card-accent-excelente'
            desarrollo.icon = 'fa-baby'
        elif promedio >= 3.0:
            desarrollo.badge = 'Bueno'
            desarrollo.accent = 'card-accent-muybueno'
            desarrollo.icon = 'fa-child'
        elif promedio >= 2.0:
            desarrollo.badge = 'Regular'
            desarrollo.accent = 'card-accent-regular'
            desarrollo.icon = 'fa-meh'
        else:
            desarrollo.badge = 'Necesita Apoyo'
            desarrollo.accent = 'card-accent-malo'
            desarrollo.icon = 'fa-frown'

        desarrollo.promedio_redondeado = round(promedio, 1)

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
        'nino_filtrado': nino_filtrado, # Pasamos el objeto del niño a la plantilla
        'filtros': filtros,
    })

@login_required
def generar_evaluacion_mensual(request):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    try:
        hogar_madre = HogarComunitario.objects.get(madre__usuario=request.user)
    except HogarComunitario.DoesNotExist:
        messages.error(request, "No tienes un hogar comunitario asignado.")
        return redirect('madre_dashboard')

    ninos_del_hogar = Nino.objects.filter(hogar=hogar_madre)

    if request.method == 'POST':
        nino_id = request.POST.get('nino')
        mes_str = request.POST.get('mes') # Formato YYYY-MM

        if not nino_id or not mes_str:
            messages.error(request, "Debes seleccionar un niño y un mes para generar la evaluación.")
            return redirect('desarrollo:generar_evaluacion')

        try:
            year, month = map(int, mes_str.split('-'))
            # Usamos el último día del mes para la fecha de referencia
            last_day = calendar.monthrange(year, month)[1]
            fecha_fin_mes = datetime(year, month, last_day).date()
        except ValueError:
            messages.error(request, "El formato del mes no es válido.")
            return redirect('desarrollo:generar_evaluacion')

        # Validar que no exista ya una evaluación para ese niño y mes
        nino = get_object_or_404(Nino, id=nino_id)
        if DesarrolloNino.objects.filter(nino_id=nino_id, fecha_fin_mes=fecha_fin_mes).exists():
            messages.warning(request, f"Ya existe una evaluación para {nino.nombres} en el mes seleccionado.")
            return redirect(reverse('desarrollo:listar_desarrollos') + f'?nino={nino_id}')

        # Crear la instancia. El método save() llamará al servicio de generación automática.
        try:
            nino = Nino.objects.get(id=nino_id)
            evaluacion = DesarrolloNino.objects.create(nino=nino, fecha_fin_mes=fecha_fin_mes)
            messages.success(request, f"Evaluación para {nino.nombres} del mes de {mes_str} generada exitosamente.")
            return redirect('desarrollo:ver_desarrollo', id=evaluacion.id)
        except Exception as e:
            messages.error(request, f"Ocurrió un error al generar la evaluación: {e}")
            return redirect('desarrollo:generar_evaluacion')

    return render(request, 'madre/desarrollo_form.html', {
        'ninos': ninos_del_hogar,
        'titulo_form': 'Generar Evaluación Mensual Automática',
        'form_action': reverse('desarrollo:generar_evaluacion'),
    })

@login_required
def ver_desarrollo(request, id):
    if request.user.rol.nombre_rol not in ['madre_comunitaria', 'padre']:
        return redirect('role_redirect')

    desarrollo = get_object_or_404(DesarrolloNino, id=id)

    # Seguridad
    if request.user.rol.nombre_rol == 'madre_comunitaria':
        if desarrollo.nino.hogar.madre.usuario != request.user:
            return redirect('desarrollo:listar_desarrollos')
    elif request.user.rol.nombre_rol == 'padre':
        if desarrollo.nino.padre.usuario != request.user:
            return redirect('padre_dashboard')

    return render(request, 'madre/desarrollo_detail.html', {'desarrollo': desarrollo})


@login_required
def editar_desarrollo(request, id):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    desarrollo = get_object_or_404(DesarrolloNino, id=id)

    # Seguridad: la madre solo puede editar registros de su hogar.
    if desarrollo.nino.hogar.madre.usuario != request.user:
        return redirect('desarrollo:listar_desarrollos')

    if request.method == 'POST':
        # Solo se actualizan los campos manuales
        desarrollo.observaciones_adicionales = request.POST.get('observaciones_adicionales', '').strip()
        desarrollo.recomendaciones_personales = request.POST.get('recomendaciones_personales', '').strip()
        
        # Usamos update_fields para ser eficientes y evitar re-llamar al generador
        desarrollo.save(update_fields=['observaciones_adicionales', 'recomendaciones_personales'])

        messages.success(request, "Las observaciones y recomendaciones han sido guardadas.")
        return redirect('desarrollo:ver_desarrollo', id=desarrollo.id)

    return render(request, 'madre/desarrollo_form.html', {
        'desarrollo': desarrollo,
        'form_action': reverse('desarrollo:editar_desarrollo', args=[id]),
        'titulo_form': f'Editar Observaciones para {desarrollo.nino.nombres}',
        'edit_mode': True, # Para diferenciar en la plantilla
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
    messages.error(request, "¡El registro de desarrollo ha sido eliminado correctamente!")
    
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

# -----------------------------------------------------------------
# CRUD SEGUIMIENTO DIARIO PARA MADRE COMUNITARIA
# -----------------------------------------------------------------
@login_required
def registrar_seguimiento_diario(request):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    try:
        hogar_madre = HogarComunitario.objects.get(madre__usuario=request.user)
    except HogarComunitario.DoesNotExist:
        return render(request, 'madre/seguimiento_diario_form.html', {'error': 'No tienes un hogar asignado.'})

    # --- Lógica para guardar el formulario (POST) ---
    if request.method == 'POST':
        fecha_str = request.POST.get('fecha')
        nino_id = request.POST.get('nino')

        # Validaciones iniciales
        if not nino_id:
            return render(request, 'madre/seguimiento_diario_form.html', {
                'error': "Por favor, selecciona un niño.",
                'fecha_filtro': fecha_str,
            })

        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return render(request, 'madre/seguimiento_diario_form.html', {'error': 'La fecha proporcionada no es válida.'})

        nino = get_object_or_404(Nino, id=nino_id, hogar=hogar_madre)

        # 1. Validar si existe planeación para la fecha
        planeacion_del_dia = PlaneacionModel.objects.filter(madre=hogar_madre.madre.usuario, fecha=fecha_obj).first()
        if not planeacion_del_dia:
            return render(request, 'madre/seguimiento_diario_form.html', {
                'error': f"No hay actividad planeada para el día {fecha_str}. No se puede registrar seguimiento.",
                'fecha_filtro': fecha_str,
            })

        # 2. Validar asistencia del niño
        asistencia = nino.asistencias.filter(fecha=fecha_obj).first()
        if not asistencia or asistencia.estado != 'Presente':
            return render(request, 'madre/seguimiento_diario_form.html', {
                'error': f"El niño {nino.nombres} no asistió el {fecha_str}, no se puede registrar seguimiento.",
                'fecha_filtro': fecha_str,
                'planeacion': planeacion_del_dia,
            })

        # 3. Validar que no exista un seguimiento duplicado
        if SeguimientoDiario.objects.filter(nino=nino, fecha=fecha_obj).exists():
            return render(request, 'madre/seguimiento_diario_form.html', {
                'error': f"Ya existe un seguimiento para {nino.nombres} en esta fecha.",
                'fecha_filtro': fecha_str,
                'planeacion': planeacion_del_dia,
                # FIX: Pasar el niño preseleccionado para que el botón "volver" funcione
                'nino_preseleccionado': nino,
                'paso': 'registrar_datos', # Para mantener la vista del formulario
                'ninos_para_seleccionar': [nino], # Para que el select no falle
            })
        # Crear el registro de seguimiento
        # Crear el registro
        SeguimientoDiario.objects.create(
            nino=nino,
            planeacion=planeacion_del_dia,
            fecha=fecha_obj,
            participacion=request.POST.get('participacion'),
            comportamiento_logro=request.POST.get('comportamiento_logro'),
            observaciones=request.POST.get('observaciones'),
            valoracion=request.POST.get('valoracion')
        )
        messages.success(request, f"¡Seguimiento para {nino.nombres} registrado correctamente!")
        redirect_url = reverse('desarrollo:listar_seguimientos')
        return redirect(f'{redirect_url}?nino={nino_id}&exito=1')

    # --- Lógica para mostrar el formulario (GET) ---
    fecha_str = request.GET.get('fecha')
    nino_id_preseleccionado = request.GET.get('nino')
    context = {
        'titulo_form': 'Registrar Seguimiento Diario',
        'fecha_filtro': fecha_str,
        'nino_preseleccionado': None, # Inicializamos
    }

    # Si se preselecciona un niño (ej: desde la gestión), lo obtenemos y lo pasamos al contexto.
    if nino_id_preseleccionado:
        try:
            context['nino_preseleccionado'] = Nino.objects.get(id=nino_id_preseleccionado, hogar=hogar_madre)
        except Nino.DoesNotExist:
            pass # Si el niño no existe o no pertenece al hogar, simplemente no se preselecciona.

    # Si no se ha seleccionado una fecha, simplemente mostramos el selector de fecha.
    if not fecha_str:
        return render(request, 'madre/seguimiento_diario_form.html', context)

    # --- A partir de aquí, asumimos que SÍ hay una fecha ---
    fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()

    planeacion_del_dia = PlaneacionModel.objects.filter(madre=hogar_madre.madre.usuario, fecha=fecha_obj).first()
    if not planeacion_del_dia:
        context['error'] = f"No hay actividad planeada para este día ({fecha_str}). No se puede registrar seguimiento."
        return render(request, 'madre/seguimiento_diario_form.html', context)

    # --- Verificación de asistencia específica si viene un niño preseleccionado ---
    if context.get('nino_preseleccionado'):
        nino_obj = context['nino_preseleccionado']
        asistencia = nino_obj.asistencias.filter(fecha=fecha_obj).first()
        
        if not asistencia:
            context['error'] = f"No se puede registrar seguimiento: Aún no se ha registrado la asistencia de {nino_obj.nombres} para el día {fecha_str}."
            return render(request, 'madre/seguimiento_diario_form.html', context) # Detiene y muestra el error

        # FIX: Validar si ya existe un seguimiento para este niño en esta fecha
        if SeguimientoDiario.objects.filter(nino=nino_obj, fecha=fecha_obj).exists():
            context['error'] = f"Ya existe un seguimiento registrado para {nino_obj.nombres} en la fecha {fecha_str}."
            # No mostramos el formulario de registro si ya existe.
            return render(request, 'madre/seguimiento_diario_form.html', context)

        
        if asistencia.estado != 'Presente':
            context['error'] = f"No se puede registrar seguimiento: El niño {nino_obj.nombres} fue registrado como '{asistencia.estado}' el día {fecha_str}."
            return render(request, 'madre/seguimiento_diario_form.html', context) # Detiene y muestra el error


    ninos_del_hogar = Nino.objects.filter(hogar=hogar_madre)
    ninos_disponibles = []
    for nino in ninos_del_hogar:
        asistio = nino.asistencias.filter(fecha=fecha_obj, estado='Presente').exists()
        ya_tiene_seguimiento = SeguimientoDiario.objects.filter(nino=nino, fecha=fecha_obj).exists()
        if asistio and not ya_tiene_seguimiento:
            ninos_disponibles.append(nino)

    # Si hay un niño preseleccionado que no está en la lista de disponibles, no mostramos el mensaje genérico.
    context.update({
        'planeacion': planeacion_del_dia,
        'ninos_para_seleccionar': ninos_disponibles,
        'paso': 'registrar_datos'
    })

    if not ninos_disponibles:
        if not context.get('nino_preseleccionado'):
            context['info'] = f"Todos los niños que asistieron el {fecha_str} ya tienen su seguimiento registrado o no hay niños disponibles."

    return render(request, 'madre/seguimiento_diario_form.html', context)

@login_required
def listar_seguimientos(request):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    try:
        hogar_madre = HogarComunitario.objects.get(madre__usuario=request.user)
    except HogarComunitario.DoesNotExist:
        return render(request, 'madre/seguimiento_diario_list.html', {'error': 'No tienes un hogar asignado.'})

    nino_id_filtro = request.GET.get('nino')
    fecha_str = request.GET.get('fecha')
    nino_filtrado = None

    # La consulta base siempre filtra por el hogar de la madre
    seguimientos = SeguimientoDiario.objects.filter(nino__hogar=hogar_madre).select_related('nino')

    # Si se especifica un niño, se convierte en el filtro principal
    if nino_id_filtro:
        seguimientos = seguimientos.filter(nino__id=nino_id_filtro)
        try:
            nino_filtrado = Nino.objects.get(id=nino_id_filtro)
        except Nino.DoesNotExist:
            pass # No se encontró el niño

    # Si se especifica una fecha, se usa como filtro secundario
    if fecha_str:
        try:
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            seguimientos = seguimientos.filter(fecha=fecha_obj)
        except (ValueError, TypeError):
            fecha_str = None # Ignorar fecha inválida
    else:
        # Si no hay fecha, no se filtra por fecha, mostrando todos los seguimientos del niño (si aplica)
        fecha_str = None

    return render(request, 'madre/seguimiento_diario_list.html', {
        'seguimientos': seguimientos.order_by('-fecha'),
        'fecha_filtro': fecha_str,
        'nino_id_filtro': nino_id_filtro,
        'nino_filtrado': nino_filtrado,
    })

@login_required
def editar_seguimiento_diario(request, id):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    seguimiento = get_object_or_404(SeguimientoDiario, id=id)

    # Verificación de seguridad: la madre solo puede editar registros de su hogar.
    if seguimiento.nino.hogar.madre.usuario != request.user:
        messages.error(request, "No tienes permiso para editar este seguimiento.")
        return redirect('desarrollo:listar_seguimientos')

    if request.method == 'POST':
        # Actualizar los campos del seguimiento con los datos del formulario
        seguimiento.participacion = request.POST.get('participacion')
        seguimiento.comportamiento_logro = request.POST.get('comportamiento_logro')
        seguimiento.observaciones = request.POST.get('observaciones', '').strip()
        seguimiento.valoracion = request.POST.get('valoracion')

        # Validación simple para campos obligatorios
        if not all([seguimiento.participacion, seguimiento.comportamiento_logro, seguimiento.valoracion]):
            return render(request, 'madre/editar_seguimiento_diario.html', {
                'error': "Error: Debes completar todos los campos obligatorios.",
                'seguimiento': seguimiento,
                'titulo_form': 'Editar Seguimiento Diario',
            })

        seguimiento.save()
        messages.success(request, f"El seguimiento para {seguimiento.nino.nombres} del {seguimiento.fecha.strftime('%d-%m-%Y')} ha sido actualizado exitosamente.")
        return redirect(reverse('desarrollo:listar_seguimientos') + f'?nino={seguimiento.nino.id}')

    return render(request, 'madre/editar_seguimiento_diario.html', {
        'seguimiento': seguimiento,
        'titulo_form': 'Editar Seguimiento Diario',
    })

@login_required
def eliminar_seguimiento(request, id):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    seguimiento = get_object_or_404(SeguimientoDiario, id=id)

    # Seguridad: solo la madre del hogar puede eliminar
    if seguimiento.nino.hogar.madre.usuario != request.user:
        return redirect('desarrollo:listar_seguimientos')

    nino_id = seguimiento.nino.id
    fecha_seguimiento = seguimiento.fecha.strftime('%Y-%m-%d')
    seguimiento.delete()
    messages.error(request, f"El seguimiento del {fecha_seguimiento} para {seguimiento.nino.nombres} ha sido eliminado.")
    
    # Redirigir a la lista de seguimientos del niño específico
    redirect_url = reverse('desarrollo:listar_seguimientos')
    return redirect(f'{redirect_url}?nino={nino_id}')

@login_required
def registrar_desarrollo(request):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('home')
    try:
        hogar_madre = HogarComunitario.objects.get(madre__usuario=request.user)
    except HogarComunitario.DoesNotExist:
        messages.error(request, 'No tienes un hogar asignado.')
        return redirect('home')
    ninos_del_hogar = Nino.objects.filter(hogar=hogar_madre)

    if request.method == 'POST':
        # Paso 1: Selección de niño y mes
        nino_id = request.POST.get('nino')
        mes_str = request.POST.get('mes')  # Formato YYYY-MM
        observaciones_adicionales = request.POST.get('observaciones_adicionales')
        recomendaciones_personales = request.POST.get('recomendaciones_personales')
        desarrollo_id = request.POST.get('desarrollo_id')

        # Si ya existe un desarrollo generado (edición de campos manuales)
        if desarrollo_id:
            desarrollo = get_object_or_404(DesarrolloNino, id=desarrollo_id)
            desarrollo.observaciones_adicionales = observaciones_adicionales
            desarrollo.recomendaciones_personales = recomendaciones_personales
            desarrollo.save(update_fields=['observaciones_adicionales', 'recomendaciones_personales'])
            messages.success(request, f'Las observaciones para {desarrollo.nino.nombres} se guardaron exitosamente.')
            # Redirigir al listado con el niño preseleccionado
            return redirect(reverse('desarrollo:listar_desarrollos') + f'?nino={desarrollo.nino.id}')

        if not nino_id or not mes_str:
            messages.error(request, 'Debes seleccionar un niño y un mes.')
            return render(request, 'madre/desarrollo_form.html', {
                'titulo_form': 'Registrar Desarrollo Mensual',
                'ninos': ninos_del_hogar,
            })
        try:
            year, month = map(int, mes_str.split('-'))
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            fecha_fin_mes = datetime(year, month, last_day).date()
        except Exception:
            messages.error(request, 'El formato del mes es inválido.')
            return render(request, 'madre/desarrollo_form.html', {
                'titulo_form': 'Registrar Desarrollo Mensual',
                'ninos': ninos_del_hogar,
            })
        nino = get_object_or_404(Nino, id=nino_id, hogar=hogar_madre)
        # Validar que no exista ya un desarrollo para ese niño y mes
        if DesarrolloNino.objects.filter(nino_id=nino_id, fecha_fin_mes=fecha_fin_mes).exists():
            mes_nombre = fecha_fin_mes.strftime("%B de %Y").capitalize()
            messages.warning(request, f'Ya existe una evaluación de desarrollo para {nino.nombres} en el mes de {mes_nombre}.')
            return redirect(reverse('desarrollo:listar_desarrollos') + f'?nino={nino_id}')
        # Crear la instancia (sin campos manuales)
        desarrollo = DesarrolloNino.objects.create(
            nino=nino,
            fecha_fin_mes=fecha_fin_mes
        )
        # Ejecutar el generador automático (ya se ejecuta en save, pero aseguramos refresco)
        from .services import GeneradorEvaluacionMensual
        GeneradorEvaluacionMensual(desarrollo).run()
        desarrollo.refresh_from_db()
        # Calcular conteos para mostrar en la plantilla
        seguimientos_mes_count = SeguimientoDiario.objects.filter(
            nino=nino,
            fecha__year=fecha_fin_mes.year,
            fecha__month=fecha_fin_mes.month
        ).count()
        novedades_mes_count = Novedad.objects.filter(
            nino=nino,
            fecha__year=fecha_fin_mes.year,
            fecha__month=fecha_fin_mes.month
        ).count()
        # Mostrar el formulario con los campos automáticos y permitir editar los manuales
        return render(request, 'madre/desarrollo_form.html', {
            'titulo_form': f'Registrar Desarrollo Mensual para {nino.nombres}',
            'ninos': ninos_del_hogar,
            'desarrollo': desarrollo,
            'edit_mode': True,
            'form_action': reverse('desarrollo:registrar_desarrollo'),
            'seguimientos_mes_count': seguimientos_mes_count,
            'novedades_mes_count': novedades_mes_count,
        })

    # GET: mostrar formulario de selección de niño y mes
    nino_preseleccionado = None
    nino_id_get = request.GET.get('nino')
    mes_get = request.GET.get('mes')

    if nino_id_get and mes_get:
        try:
            year, month = map(int, mes_get.split('-'))
            last_day = calendar.monthrange(year, month)[1]
            fecha_fin_mes = datetime(year, month, last_day).date()
            
            # Si existe un desarrollo, lo mostramos directamente
            desarrollo_existente = DesarrolloNino.objects.get(nino_id=nino_id_get, fecha_fin_mes=fecha_fin_mes)
            return render(request, 'madre/desarrollo_form.html', {'desarrollo': desarrollo_existente, 'titulo_form': 'Ver Desarrollo Mensual'})
        except (DesarrolloNino.DoesNotExist, ValueError):
            pass # Si no existe o el mes es inválido, continuamos para mostrar el form de creación

    if nino_id_get:
        nino_preseleccionado = get_object_or_404(Nino, id=nino_id_get, hogar=hogar_madre)

    return render(request, 'madre/desarrollo_form.html', {
        'titulo_form': 'Registrar Desarrollo Mensual',
        'ninos': ninos_del_hogar,
        'nino_preseleccionado': nino_preseleccionado,
    })
