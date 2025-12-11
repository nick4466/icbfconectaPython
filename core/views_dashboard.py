"""
Vistas del Dashboard Administrativo - ICBF Conecta
Incluye estadísticas, gráficas y gestión avanzada de hogares
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
import json

from .models import (
    HogarComunitario, 
    MadreComunitaria, 
    Nino, 
    Usuario,
    VisitaTecnica,
    ActaVisitaTecnica,
    SolicitudMatriculacion
)
from .decorators import rol_requerido


@login_required
def dashboard_admin(request):
    """
    Dashboard principal del administrador
    Muestra estadísticas generales, gráficas y tablas de resumen
    """
    
    # ========== ESTADÍSTICAS GENERALES ==========
    hoy = timezone.now()
    hace_30_dias = hoy - timedelta(days=30)
    primer_dia_mes = hoy.replace(day=1)
    
    # Total de hogares activos (estado 'activo')
    total_hogares = HogarComunitario.objects.filter(
        estado='activo'
    ).count()
    
    # Nuevos hogares este mes
    nuevos_hogares_mes = HogarComunitario.objects.filter(
        fecha_registro__gte=primer_dia_mes
    ).count()
    
    # Total de agentes educativos
    total_agentes = MadreComunitaria.objects.count()
    agentes_activos = MadreComunitaria.objects.filter(
        hogares_asignados__estado='activo'
    ).distinct().count()
    
    # Total de niños matriculados
    total_ninos = Nino.objects.filter(estado='activo').count()
    
    # Capacidad total del sistema (usar campo capacidad real, no promedio fijo)
    from django.db.models import Sum
    capacidad_total = HogarComunitario.objects.filter(
        estado='activo'
    ).aggregate(total=Sum('capacidad'))['total'] or 0
    
    # Solicitudes pendientes (si existe el modelo)
    try:
        solicitudes_pendientes = SolicitudMatriculacion.objects.filter(
            estado='pendiente'
        ).count()
    except:
        solicitudes_pendientes = 0
    
    # Visitas programadas próximas 30 días
    try:
        visitas_proximas = VisitaTecnica.objects.filter(
            fecha_visita__gte=hoy,
            fecha_visita__lte=hoy + timedelta(days=30),
            estado__in=['programada', 'pendiente']
        ).count()
    except:
        visitas_proximas = 0
    
    # Visitas vencidas
    try:
        visitas_vencidas = VisitaTecnica.objects.filter(
            fecha_visita__lt=hoy,
            estado='pendiente'
        ).count()
    except:
        visitas_vencidas = 0
    
    stats = {
        'total_hogares': total_hogares,
        'nuevos_hogares_mes': nuevos_hogares_mes,
        'total_agentes': total_agentes,
        'agentes_activos': agentes_activos,
        'total_ninos': total_ninos,
        'capacidad_total': capacidad_total,
        'solicitudes_pendientes': solicitudes_pendientes,
        'visitas_proximas': visitas_proximas,
        'visitas_vencidas': visitas_vencidas,
    }
    
    # ========== GRÁFICA: MATRÍCULAS POR MES ==========
    # Últimos 6 meses
    chart_matriculas = generar_chart_matriculas()
    
    # ========== GRÁFICA: ESTADOS DE HOGARES ==========
    chart_estados = generar_chart_estados()
    
    # ========== GRÁFICA: TOP 10 HOGARES ==========
    chart_top_hogares = generar_chart_top_hogares()
    
    # ========== GRÁFICA: SOLICITUDES ==========
    chart_solicitudes = generar_chart_solicitudes()
    
    # ========== TABLA: HOGARES RECIENTES ==========
    hogares_recientes = HogarComunitario.objects.select_related(
        'madre__usuario'
    ).annotate(
        ninos_count=Count('ninos', filter=Q(ninos__estado='activo'))
    ).order_by('-fecha_registro')[:15]
    
    # Agregar última visita a cada hogar
    for hogar in hogares_recientes:
        try:
            ultima_visita = VisitaTecnica.objects.filter(
                hogar=hogar
            ).order_by('-fecha_visita').first()
            hogar.ultima_visita = ultima_visita.fecha_visita if ultima_visita else None
        except:
            hogar.ultima_visita = None
    
    context = {
        'stats': stats,
        'chart_matriculas': chart_matriculas,
        'chart_estados': chart_estados,
        'chart_top_hogares': chart_top_hogares,
        'chart_solicitudes': chart_solicitudes,
        'hogares_recientes': hogares_recientes,
    }
    
    return render(request, 'admin/dashboard_admin.html', context)


def generar_chart_matriculas():
    """
    Genera datos para gráfica de matrículas por mes
    Últimos 6 meses
    """
    hoy = timezone.now()
    labels = []
    data = []
    
    for i in range(5, -1, -1):  # Últimos 6 meses
        mes = hoy - timedelta(days=30*i)
        inicio_mes = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calcular fin de mes
        if mes.month == 12:
            fin_mes = mes.replace(year=mes.year+1, month=1, day=1)
        else:
            fin_mes = mes.replace(month=mes.month+1, day=1)
        
        # Contar niños matriculados en ese mes
        count = Nino.objects.filter(
            fecha_ingreso__gte=inicio_mes,
            fecha_ingreso__lt=fin_mes
        ).count()
        
        # Formatear nombre del mes
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        labels.append(meses[mes.month - 1])
        data.append(count)
    
    return {
        'labels': json.dumps(labels),
        'data': json.dumps(data)
    }


def generar_chart_estados():
    """
    Genera datos para gráfica de estados de hogares
    """
    estados_map = {
        'activo': 'Activos',
        'pendiente_visita': 'Pendiente Visita',
        'en_revision': 'En Revisión',
        'rechazado': 'Rechazados',
        'aprobado': 'Aprobados'
    }
    
    labels = []
    data = []
    
    for estado_key, estado_label in estados_map.items():
        count = HogarComunitario.objects.filter(estado=estado_key).count()
        if count > 0:
            labels.append(estado_label)
            data.append(count)
    
    return {
        'labels': json.dumps(labels),
        'data': json.dumps(data)
    }


def generar_chart_top_hogares():
    """
    Top 10 hogares con más niños matriculados
    """
    hogares = HogarComunitario.objects.annotate(
        ninos_count=Count('ninos', filter=Q(ninos__estado='activo'))
    ).filter(
        ninos_count__gt=0
    ).order_by('-ninos_count')[:10]
    
    labels = [h.nombre_hogar[:20] for h in hogares]
    data = [h.ninos_count for h in hogares]
    
    return {
        'labels': json.dumps(labels),
        'data': json.dumps(data)
    }


def generar_chart_solicitudes():
    """
    Gráfica de solicitudes: Aprobadas vs Rechazadas vs Pendientes
    """
    try:
        aprobadas = SolicitudMatriculacion.objects.filter(estado='aprobada').count()
        rechazadas = SolicitudMatriculacion.objects.filter(estado='rechazada').count()
        pendientes = SolicitudMatriculacion.objects.filter(estado='pendiente').count()
        
        data = [aprobadas, rechazadas, pendientes]
    except:
        # Si no existe el modelo Solicitud, usar datos de ejemplo
        data = [0, 0, 0]
    
    return {
        'data': json.dumps(data)
    }


@login_required
def hogares_dashboard(request):
    """
    Vista de gestión completa de hogares
    Incluye filtros, búsqueda y vista por localidad
    """
    
    # Filtros desde GET params
    localidad = request.GET.get('localidad', '')
    estado = request.GET.get('estado', '')
    busqueda = request.GET.get('q', '')
    
    # Query base
    hogares = HogarComunitario.objects.select_related(
        'madre__usuario', 'regional', 'ciudad'
    ).annotate(
        ninos_count=Count('ninos', filter=Q(ninos__estado='activo'))
    )
    
    # Aplicar filtros
    if localidad:
        hogares = hogares.filter(localidad__icontains=localidad)
    
    if estado:
        hogares = hogares.filter(estado=estado)
    
    if busqueda:
        hogares = hogares.filter(
            Q(nombre_hogar__icontains=busqueda) |
            Q(madre__usuario__nombres__icontains=busqueda) |
            Q(madre__usuario__apellidos__icontains=busqueda) |
            Q(direccion__icontains=busqueda)
        )
    
    hogares = hogares.order_by('-fecha_registro')
    
    # Obtener localidades únicas para filtro
    localidades = HogarComunitario.objects.values_list(
        'localidad', flat=True
    ).distinct().order_by('localidad')
    
    # Agrupar hogares por localidad
    hogares_por_localidad = {}
    for hogar in hogares:
        loc = hogar.localidad or 'Sin localidad'
        if loc not in hogares_por_localidad:
            hogares_por_localidad[loc] = []
        hogares_por_localidad[loc].append(hogar)
    
    context = {
        'hogares': hogares,
        'hogares_por_localidad': hogares_por_localidad,
        'localidades': localidades,
        'filtro_localidad': localidad,
        'filtro_estado': estado,
        'busqueda': busqueda,
    }
    
    return render(request, 'admin/hogares_dashboard.html', context)


@login_required
def hogar_detalle_api(request, hogar_id):
    """
    API para obtener detalles completos de un hogar (JSON)
    Usado por el modal de vista de hogar
    """
    try:
        hogar = get_object_or_404(HogarComunitario, id=hogar_id)
        madre = hogar.madre
        usuario_madre = madre.usuario
        
        # Contar niños totales (activos y eliminados)
        ninos_activos = Nino.objects.filter(hogar=hogar, estado='activo')
        ninos_eliminados = Nino.objects.filter(hogar=hogar, estado='eliminado')
        ninos_total_matriculados = Nino.objects.filter(hogar=hogar).count()
        
        # Formatear fechas en español de manera segura
        meses_espanol = {
            'January': 'enero', 'February': 'febrero', 'March': 'marzo',
            'April': 'abril', 'May': 'mayo', 'June': 'junio',
            'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
            'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
        }
        
        fecha_str = hogar.fecha_registro.strftime('%d de %B de %Y')
        for eng, esp in meses_espanol.items():
            fecha_str = fecha_str.replace(eng, esp)
        
        # Información del hogar
        data = {
            'id': hogar.id,
            'nombre_hogar': hogar.nombre_hogar,
            'responsable': f"{usuario_madre.nombres} {usuario_madre.apellidos}",
            'direccion': hogar.direccion,
            'localidad': hogar.localidad_bogota.nombre if hogar.localidad_bogota else (hogar.localidad or 'No especificado'),
            'barrio': hogar.barrio or 'No especificado',
            'estrato': str(hogar.estrato) if hogar.estrato else 'No especificado',
            'estado': hogar.get_estado_display(),
            'fecha_registro': hogar.fecha_registro.strftime('%d/%m/%Y %H:%M'),
            'fecha_creacion': fecha_str,
            'capacidad_maxima': hogar.capacidad_maxima,
            'capacidad_calculada': hogar.capacidad_calculada or 'No calculada',
            'area_social_m2': str(hogar.area_social_m2) if hogar.area_social_m2 else 'No especificado',
            'tipo_tenencia': hogar.get_tipo_tenencia_display() if hogar.tipo_tenencia else 'No especificado',
            
            # Información de la madre comunitaria
            'madre': {
                'nombres': usuario_madre.nombres,
                'apellidos': usuario_madre.apellidos,
                'documento': usuario_madre.documento,
                'email': usuario_madre.correo or 'No especificado',
                'telefono': usuario_madre.telefono or 'No especificado',
                'nivel_escolaridad': madre.nivel_escolaridad or 'No especificado',
                'titulo_obtenido': madre.titulo_obtenido or 'No especificado',
                'institucion': madre.institucion or 'No especificado',
                'experiencia_previa': madre.experiencia_previa or 'Sin experiencia previa registrada',
                'foto': madre.foto_madre.url if madre.foto_madre else (usuario_madre.foto_admin.url if usuario_madre.foto_admin else None),
            },
            
            # Estadísticas de niños
            'estadisticas_ninos': {
                'activos': ninos_activos.count(),
                'eliminados': ninos_eliminados.count(),
                'total_matriculados': ninos_total_matriculados,
            },
            
            # Fotos del hogar
            'fotos': {
                'interior': hogar.fotos_interior.url if hogar.fotos_interior else None,
                'exterior': hogar.fotos_exterior.url if hogar.fotos_exterior else None,
            },
            
            # Infraestructura
            'infraestructura': {
                'num_habitaciones': str(hogar.num_habitaciones) if hogar.num_habitaciones else 'No especificado',
                'num_banos': str(hogar.num_banos) if hogar.num_banos else 'No especificado',
                'material_construccion': hogar.material_construccion or 'No especificado',
                'riesgos_cercanos': hogar.riesgos_cercanos or 'Ninguno registrado',
            },
            
            'ninos': [],
            'total_visitas': 0,
            'ultima_visita': None,
            'proxima_visita': None,
        }
        
        # Niños del hogar
        for nino in ninos_activos:
            data['ninos'].append({
                'id': nino.id,
                'nombres': nino.nombres,
                'apellidos': nino.apellidos,
                'edad': calcular_edad(nino.fecha_nacimiento),
                'foto': nino.foto.url if nino.foto else None,
            })
        
        # Visitas técnicas
        try:
            visitas = VisitaTecnica.objects.filter(hogar=hogar, estado='completada')
            data['total_visitas'] = visitas.count()
            ultima = visitas.order_by('-fecha_realizacion').first()
            if ultima and ultima.fecha_realizacion:
                data['ultima_visita'] = ultima.fecha_realizacion.strftime('%d/%m/%Y')
        except Exception as e:
            # En caso de error, mantener valores por defecto
            print(f"Error al cargar visitas: {e}")
        
        # Próxima visita programada
        if hogar.proxima_visita:
            data['proxima_visita'] = hogar.proxima_visita.strftime('%d/%m/%Y')
        
        return JsonResponse(data)
        
    except Exception as e:
        # Capturar cualquier error y retornar un JSON con el error
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error en hogar_detalle_api: {error_trace}")
        return JsonResponse({
            'error': True,
            'mensaje': str(e),
            'detalle': error_trace
        }, status=500)


@login_required
@rol_requerido('administrador')
def hogar_historial_visitas_api(request, hogar_id):
    """
    API para obtener el historial completo de visitas técnicas de un hogar
    Incluye toda la información del acta de visita
    """
    hogar = get_object_or_404(HogarComunitario, id=hogar_id)
    
    # Obtener todas las visitas del hogar ordenadas por fecha
    # select_related se usa para OneToOneField y ForeignKey
    visitas = VisitaTecnica.objects.filter(hogar=hogar).select_related(
        'visitador', 'creado_por'
    ).order_by('-fecha_programada')
    
    data = {
        'hogar_id': hogar.id,
        'nombre_hogar': hogar.nombre_hogar,
        'visitas': []
    }
    
    for visita in visitas:
        visita_data = {
            'id': visita.id,
            'tipo_visita': visita.tipo_visita,
            'tipo_visita_display': visita.get_tipo_visita_display(),
            'estado': visita.estado,
            'fecha_programada': visita.fecha_programada.strftime('%d/%m/%Y %H:%M'),
            'fecha_realizacion': visita.fecha_realizacion.strftime('%d/%m/%Y %H:%M') if visita.fecha_realizacion else None,
            'visitador': f"{visita.visitador.nombres} {visita.visitador.apellidos}" if visita.visitador else 'No asignado',
            'creado_por': f"{visita.creado_por.nombres} {visita.creado_por.apellidos}" if visita.creado_por else 'Sistema',
            'observaciones_agenda': visita.observaciones_agenda or '',
            'observaciones_visita': hogar.observaciones_visita or '',  # Observaciones del formulario de activación
            'fecha_creacion': visita.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'acta': None
        }
        
        # Si tiene acta completada, agregar toda la información
        try:
            acta = visita.acta
            visita_data['acta'] = {
                # Geolocalización
                'geolocalizacion_lat_verificada': str(acta.geolocalizacion_lat_verificada),
                'geolocalizacion_lon_verificada': str(acta.geolocalizacion_lon_verificada),
                'direccion_verificada': acta.direccion_verificada,
                'direccion_coincide': acta.direccion_coincide,
                'observaciones_direccion': acta.observaciones_direccion or '',
                'estrato_verificado': acta.estrato_verificado,
                'estrato_coincide': acta.estrato_coincide,
                
                # Servicios públicos
                'tiene_agua_potable': acta.tiene_agua_potable,
                'agua_continua': acta.agua_continua,
                'agua_legal': acta.agua_legal,
                'tiene_energia': acta.tiene_energia,
                'energia_continua': acta.energia_continua,
                'energia_legal': acta.energia_legal,
                'tiene_alcantarillado': acta.tiene_alcantarillado,
                'manejo_excretas_adecuado': acta.manejo_excretas_adecuado,
                
                # Infraestructura
                'estado_pisos': acta.estado_pisos,
                'estado_pisos_display': acta.get_estado_pisos_display(),
                'estado_paredes': acta.estado_paredes,
                'estado_paredes_display': acta.get_estado_paredes_display(),
                'estado_techos': acta.estado_techos,
                'estado_techos_display': acta.get_estado_techos_display(),
                'ventilacion_adecuada': acta.ventilacion_adecuada,
                'iluminacion_natural_adecuada': acta.iluminacion_natural_adecuada,
                'observaciones_infraestructura': acta.observaciones_infraestructura or '',
                
                # Riesgos
                'proximidad_rios': acta.proximidad_rios,
                'proximidad_deslizamientos': acta.proximidad_deslizamientos,
                'proximidad_trafico_intenso': acta.proximidad_trafico_intenso,
                'proximidad_contaminacion': acta.proximidad_contaminacion,
                'nivel_riesgo_general': acta.nivel_riesgo_general,
                'nivel_riesgo_general_display': acta.get_nivel_riesgo_general_display(),
                'descripcion_riesgos': acta.descripcion_riesgos or '',
                
                # Áreas y capacidad
                'area_social_largo': str(acta.area_social_largo),
                'area_social_ancho': str(acta.area_social_ancho),
                'area_social_total': str(acta.area_social_total),
                'tiene_patio_cubierto': acta.tiene_patio_cubierto,
                'patio_largo': str(acta.patio_largo) if acta.patio_largo else None,
                'patio_ancho': str(acta.patio_ancho) if acta.patio_ancho else None,
                'patio_total': str(acta.patio_total) if acta.patio_total else None,
                'capacidad_calculada': acta.capacidad_calculada,
                'capacidad_recomendada': acta.capacidad_recomendada,
                'justificacion_capacidad': acta.justificacion_capacidad or '',
                
                # Baños
                'num_banos_verificado': acta.num_banos_verificado,
                'estado_higiene_banos': acta.estado_higiene_banos,
                'estado_higiene_banos_display': acta.get_estado_higiene_banos_display(),
                
                # Resultado
                'resultado_visita': acta.resultado_visita,
                'resultado_visita_display': acta.get_resultado_visita_display(),
                'observaciones_generales': acta.observaciones_generales,
                'recomendaciones': acta.recomendaciones or '',
                'condiciones_aprobacion': acta.condiciones_aprobacion or '',
                
                # Fechas
                'fecha_creacion': acta.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'completado_por': f"{acta.completado_por.nombres} {acta.completado_por.apellidos}" if acta.completado_por else 'Sistema'
            }
        except ActaVisitaTecnica.DoesNotExist:
            # Si no tiene acta, visita_data['acta'] ya está en None
            pass
        
        data['visitas'].append(visita_data)
    
    return JsonResponse(data)


@login_required
def nino_detalle_api(request, nino_id):
    """
    API para obtener detalles completos de un niño (JSON)
    Incluye información del tutor y documentos
    """
    nino = get_object_or_404(Nino, id=nino_id)
    
    data = {
        'id': nino.id,
        'nombres': nino.nombres,
        'apellidos': nino.apellidos,
        'documento': nino.numero_documento,
        'fecha_nacimiento': nino.fecha_nacimiento.strftime('%d/%m/%Y'),
        'edad': calcular_edad(nino.fecha_nacimiento),
        'genero': nino.get_genero_display(),
        'foto': nino.foto.url if nino.foto else None,
        'fecha_ingreso': nino.fecha_ingreso.strftime('%d/%m/%Y'),
        'estado': nino.estado,
        'hogar': {
            'id': nino.hogar.id,
            'nombre': nino.hogar.nombre_hogar,
        },
        'tutor': {},
        'documentos': [],
    }
    
    # Información del tutor/padre
    if hasattr(nino, 'padre'):
        padre = nino.padre
        data['tutor'] = {
            'nombres': padre.usuario.nombres,
            'apellidos': padre.usuario.apellidos,
            'documento': padre.usuario.documento,
            'telefono': padre.usuario.telefono,
            'parentesco': padre.parentesco if hasattr(padre, 'parentesco') else 'Padre/Madre',
            'ocupacion': padre.ocupacion if hasattr(padre, 'ocupacion') else '',
            'situacion_economica': padre.situacion_economica if hasattr(padre, 'situacion_economica') else '',
        }
    
    # Documentos del niño
    # Aquí agregar lógica para obtener documentos (certificados, fotos, etc.)
    documentos_fields = [
        ('registro_civil', 'Registro Civil'),
        ('carnet_vacunas', 'Carnet de Vacunas'),
        ('certificado_salud', 'Certificado de Salud'),
    ]
    
    for field, nombre in documentos_fields:
        if hasattr(nino, field) and getattr(nino, field):
            archivo = getattr(nino, field)
            data['documentos'].append({
                'nombre': nombre,
                'url': archivo.url,
                'tipo': obtener_tipo_archivo(archivo.name)
            })
    
    return JsonResponse(data)


@login_required
def preview_document(request, tipo, id, campo):
    """
    Vista para previsualizar documentos PDF/Imágenes
    Retorna HTML con visor embebido
    """
    # Obtener el objeto y archivo según el tipo
    if tipo == 'hogar':
        obj = get_object_or_404(HogarComunitario, id=id)
    elif tipo == 'nino':
        obj = get_object_or_404(Nino, id=id)
    elif tipo == 'madre':
        obj = get_object_or_404(MadreComunitaria, id=id)
    else:
        return JsonResponse({'error': 'Tipo no válido'}, status=400)
    
    # Obtener el archivo del campo especificado
    if not hasattr(obj, campo):
        return JsonResponse({'error': 'Campo no existe'}, status=400)
    
    archivo = getattr(obj, campo)
    if not archivo:
        return JsonResponse({'error': 'Archivo no encontrado'}, status=404)
    
    # Determinar tipo de archivo
    extension = archivo.name.split('.')[-1].lower()
    tipo_archivo = obtener_tipo_archivo(archivo.name)
    
    context = {
        'archivo_url': archivo.url,
        'tipo_archivo': tipo_archivo,
        'nombre_archivo': archivo.name.split('/')[-1],
    }
    
    return render(request, 'admin/preview_document.html', context)


# ========== FUNCIONES AUXILIARES ==========

def calcular_edad(fecha_nacimiento):
    """Calcula la edad en años a partir de una fecha de nacimiento"""
    hoy = timezone.now().date()
    edad = hoy.year - fecha_nacimiento.year
    
    # Ajustar si no ha cumplido años este año
    if hoy.month < fecha_nacimiento.month or \
       (hoy.month == fecha_nacimiento.month and hoy.day < fecha_nacimiento.day):
        edad -= 1
    
    return edad


def obtener_tipo_archivo(nombre_archivo):
    """Determina el tipo de archivo por extensión"""
    extension = nombre_archivo.split('.')[-1].lower()
    
    if extension == 'pdf':
        return 'pdf'
    elif extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        return 'imagen'
    elif extension in ['doc', 'docx']:
        return 'word'
    elif extension in ['xls', 'xlsx']:
        return 'excel'
    else:
        return 'otro'


@login_required
def nino_carpeta_view(request, nino_id):
    """
    Vista completa tipo carpeta de un niño
    Muestra toda la información, tutor y documentos
    """
    nino = get_object_or_404(Nino, id=nino_id)
    
    # Información del tutor
    tutor = None
    if hasattr(nino, 'padre'):
        padre = nino.padre
        tutor = {
            'nombres': padre.usuario.nombres,
            'apellidos': padre.usuario.apellidos,
            'documento': padre.usuario.documento,
            'telefono': padre.usuario.telefono,
            'parentesco': padre.parentesco if hasattr(padre, 'parentesco') else 'Padre/Madre',
            'ocupacion': padre.ocupacion if hasattr(padre, 'ocupacion') else '',
            'situacion_economica': padre.situacion_economica if hasattr(padre, 'situacion_economica') else '',
        }
    
    # Documentos del niño
    documentos = []
    documentos_fields = [
        ('registro_civil', 'Registro Civil'),
        ('carnet_vacunas', 'Carnet de Vacunas'),
        ('certificado_salud', 'Certificado de Salud'),
        ('foto', 'Fotografía'),
    ]
    
    for field, nombre in documentos_fields:
        if hasattr(nino, field) and getattr(nino, field):
            archivo = getattr(nino, field)
            documentos.append({
                'nombre': nombre,
                'url': archivo.url,
                'tipo': obtener_tipo_archivo(archivo.name)
            })
    
    # Historial (ejemplo básico)
    historial = [
        {
            'fecha': nino.fecha_ingreso,
            'titulo': 'Ingreso al hogar',
            'descripcion': f'Niño ingresó al hogar {nino.hogar.nombre_hogar}'
        }
    ]
    
    context = {
        'nino': nino,
        'tutor': tutor,
        'documentos': documentos,
        'historial': historial,
    }
    
    return render(request, 'admin/nino_carpeta.html', context)
