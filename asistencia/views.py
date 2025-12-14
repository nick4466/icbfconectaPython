from django.shortcuts import render, redirect, get_object_or_404
from core.models import Nino, Asistencia
from datetime import date, timedelta
from novedades.models import Novedad
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from notifications.models import Notification  # importa el modelo
from django.contrib.auth.decorators import login_required
from core.views import rol_requerido  # si lo tienes definido ahí
from core.models import HogarComunitario
from asistencia.utils import verificar_ausencias
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa




@login_required
@rol_requerido('madre_comunitaria')
def asistencia_form(request):
    madre_profile = request.user.madre_profile
    hogar_madre = HogarComunitario.objects.filter(madre=madre_profile).first()
    ninos = Nino.objects.filter(hogar=hogar_madre)

    if request.method == 'POST':
        # DEBUG: Imprimir qué se recibe en POST
        print("\n" + "=" * 80)
        print("DEBUG POST recibido en asistencia_form:")
        print(f"POST keys: {list(request.POST.keys())}")
        print(f"POST data: {dict(request.POST)}")
        print(f"Valor de POST['fecha']: {request.POST.get('fecha')}")
        print(f"Valor de POST['end_date']: {request.POST.get('end_date')}")
        print("=" * 80 + "\n")

        # Soportar rango de fechas: `fecha` (inicio) y opcional `end_date` (fin).
        fecha_str = request.POST.get('fecha')
        end_date_str = request.POST.get('end_date')

        print(f"fecha_str (después de .get()): {fecha_str}")
        print(f"end_date_str (después de .get()): {end_date_str}\n")

        if fecha_str:
            start_date = date.fromisoformat(fecha_str)
            print(f"start_date (convertida): {start_date}")
        else:
            start_date = date.today()
            print(f"start_date (por defecto hoy): {start_date}")

        if end_date_str:
            end_date = date.fromisoformat(end_date_str)
            print(f"end_date (convertida): {end_date}")
        else:
            end_date = start_date
            print(f"end_date (igual a start_date): {end_date}")

        # Generar lista de fechas inclusivas entre start_date y end_date
        delta_days = (end_date - start_date).days
        fechas_a_guardar = [start_date]
        if delta_days > 0:
            fechas_a_guardar = [start_date]
            for i in range(1, delta_days + 1):
                fechas_a_guardar.append(start_date + __import__('datetime').timedelta(days=i))

        print(f"Fechas a guardar: {fechas_a_guardar}\n")

        # Para cada fecha del rango, guardar la asistencia seleccionada para cada niño
        for fecha_hoy in fechas_a_guardar:
            for nino in ninos:
                estado = request.POST.get(f'nino_{nino.id}')
                if estado:
                    Asistencia.objects.update_or_create(
                        nino=nino,
                        fecha=fecha_hoy,
                        defaults={'estado': estado}
                    )
                    verificar_ausencias(nino, request.user)  # Verifica ausencias después de guardar

        # 🔔 Notificaciones del usuario
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
        notif_count = notifications.filter(read=False).count()

        # Generar mensaje detallado según si es rango o día único
        num_dias = len(fechas_a_guardar)
        if num_dias == 1:
            mensaje = f"Asistencia registrada para el {start_date.strftime('%d/%m/%Y')} ✅"
        else:
            mensaje = f"Asistencia registrada para {num_dias} días ({start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}) ✅"

        # Mostrar la fecha de inicio en el formulario después de guardar
        return render(request, 'asistencia/asistencia_form.html', {
            'ninos': ninos,
            'fecha_hoy': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d') if end_date_str else '',
            'mensaje': mensaje,
            'notifications': notifications,
            'notif_count': notif_count,
        })

    fecha_hoy = date.today().strftime('%Y-%m-%d')
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    notif_count = notifications.filter(read=False).count()

    return render(request, 'asistencia/asistencia_form.html', {
        'ninos': ninos,
        'fecha_hoy': fecha_hoy,
        'notifications': notifications,
        'notif_count': notif_count,
    })




@login_required
@rol_requerido('madre_comunitaria')
def historial_asistencia(request, nino_id):
    madre_profile = request.user.madre_profile
    hogar_madre = HogarComunitario.objects.filter(madre=madre_profile).first()
    nino = get_object_or_404(Nino, id=nino_id, hogar=hogar_madre)
    historial = Asistencia.objects.filter(nino=nino).order_by('-fecha')

    # Filtro por rango
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        historial = historial.filter(fecha__range=[start_date, end_date])

    # Vincular novedad por fecha y niño
    for asistencia in historial:
        novedad = Novedad.objects.filter(nino=nino, fecha=asistencia.fecha).first()
        asistencia.novedad_id = novedad.id if novedad else None

    # Datos para calendario
    eventos = [
        {
            "title": a.estado,
            "start": a.fecha.strftime("%Y-%m-%d"),
            "color": (
                "#28a745" if a.estado == "Presente" else
                "#dc3545" if a.estado == "Ausente" else
                "#6f42c1"
            )
        }
        for a in historial
    ]

    total = historial.count()
    presentes = historial.filter(estado="Presente").count()
    ausentes = historial.filter(estado="Ausente").count()
    justificados = historial.filter(estado="Justificado").count()

    def porcentaje(valor):
        return round((valor / total) * 100) if total > 0 else 0

    # Calcular si hay ausencias críticas (umbral de 3 o más ausencias sin justificar)
    ausencias_sin_justificar = historial.filter(estado="Ausente").count()
    tiene_alerta = ausencias_sin_justificar >= 3
    
    # Contexto para mostrar alerta
    alerta_ausencias = {
        'tiene_alerta': tiene_alerta,
        'ausencias_sin_justificar': ausencias_sin_justificar,
        'nivel': 'grave' if ausencias_sin_justificar >= 5 else 'warning' if ausencias_sin_justificar >= 3 else 'info',
        'porcentaje_ausencias': porcentaje(ausentes),
    }

    return render(request, 'asistencia/historial.html', {
        'nino': nino,
        'historial': historial,
        'presentes': presentes,
        'ausentes': ausentes,
        'justificados': justificados,
        'porc_presentes': porcentaje(presentes),
        'porc_ausentes': porcentaje(ausentes),
        'porc_justificados': porcentaje(justificados),
        'eventos_json': json.dumps(eventos, cls=DjangoJSONEncoder),
        'start_date': start_date,
        'end_date': end_date,
        'alerta_ausencias': alerta_ausencias,
    })


def crear_novedad_desde_asistencia(request):
    if request.method == 'POST':
        nino_id = request.POST.get('nino_id')
        fecha = request.POST.get('fecha')
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')
        observaciones = request.POST.get('observaciones')
        archivo_pdf = request.FILES.get('archivo_pdf')

        Novedad.objects.create(
            nino_id=nino_id,
            fecha=fecha,
            tipo=tipo,
            descripcion=descripcion,
            observaciones=observaciones,
            archivo_pdf=archivo_pdf
        )

        updated = Asistencia.objects.filter(nino_id=nino_id, fecha=fecha).update(estado="Justificado")
        if not updated:
            Asistencia.objects.create(nino_id=nino_id, fecha=fecha, estado="Justificado")

        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
@rol_requerido('madre_comunitaria')
def historial_asistencia_pdf(request, nino_id):
    madre_profile = request.user.madre_profile
    hogar_madre = HogarComunitario.objects.filter(madre=madre_profile).first()
    nino = get_object_or_404(Nino, id=nino_id, hogar=hogar_madre)
    historial = Asistencia.objects.filter(nino=nino).order_by('-fecha')

    # Contexto igual al HTML
    context = {
        'nino': nino,
        'historial': historial,
        'presentes': historial.filter(estado="Presente").count(),
        'ausentes': historial.filter(estado="Ausente").count(),
        'justificados': historial.filter(estado="Justificado").count(),
    }

    template = get_template("asistencia/historial_pdf.html")  # nuevo template para PDF
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="historial_{nino.nombres}.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response


@login_required
@rol_requerido('madre_comunitaria')
def asistencia_estadisticas(request):
    """Vista para mostrar estadísticas generales de asistencia del hogar"""
    madre_profile = request.user.madre_profile
    hogar_madre = HogarComunitario.objects.filter(madre=madre_profile).first()
    ninos = Nino.objects.filter(hogar=hogar_madre)

    # Rangos de tiempo para análisis
    hoy = date.today()
    hace_30_dias = hoy - timedelta(days=30)
    hace_7_dias = hoy - timedelta(days=7)

    # Estadísticas generales (últimos 30 días)
    asistencias_30 = Asistencia.objects.filter(nino__hogar=hogar_madre, fecha__gte=hace_30_dias)
    presentes_30 = asistencias_30.filter(estado="Presente").count()
    ausentes_30 = asistencias_30.filter(estado="Ausente").count()
    justificados_30 = asistencias_30.filter(estado="Justificado").count()
    total_registros_30 = asistencias_30.count()

    # Estadísticas últimos 7 días
    asistencias_7 = asistencias_30.filter(fecha__gte=hace_7_dias)
    presentes_7 = asistencias_7.filter(estado="Presente").count()
    ausentes_7 = asistencias_7.filter(estado="Ausente").count()
    justificados_7 = asistencias_7.filter(estado="Justificado").count()

    # Cálculo de porcentajes
    porcentaje_presentes_30 = round((presentes_30 / total_registros_30 * 100)) if total_registros_30 > 0 else 0
    porcentaje_ausentes_30 = round((ausentes_30 / total_registros_30 * 100)) if total_registros_30 > 0 else 0
    porcentaje_justificados_30 = round((justificados_30 / total_registros_30 * 100)) if total_registros_30 > 0 else 0

    # Estadísticas por niño (últimos 30 días)
    estadisticas_nino = []
    for nino in ninos:
        asist_nino = Asistencia.objects.filter(nino=nino, fecha__gte=hace_30_dias)
        pres = asist_nino.filter(estado="Presente").count()
        aus = asist_nino.filter(estado="Ausente").count()
        just = asist_nino.filter(estado="Justificado").count()
        total = asist_nino.count()
        porc = round((pres / total * 100)) if total > 0 else 0

        estadisticas_nino.append({
            'nino': nino,
            'presentes': pres,
            'ausentes': aus,
            'justificados': just,
            'total': total,
            'porcentaje': porc,
        })

    # Notificaciones
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    notif_count = notifications.filter(read=False).count()

    return render(request, 'asistencia/estadisticas.html', {
        'hogar': hogar_madre,
        'ninos': ninos,
        'presentes_30': presentes_30,
        'ausentes_30': ausentes_30,
        'justificados_30': justificados_30,
        'total_registros_30': total_registros_30,
        'porcentaje_presentes_30': porcentaje_presentes_30,
        'porcentaje_ausentes_30': porcentaje_ausentes_30,
        'porcentaje_justificados_30': porcentaje_justificados_30,
        'presentes_7': presentes_7,
        'ausentes_7': ausentes_7,
        'justificados_7': justificados_7,
        'estadisticas_nino': estadisticas_nino,
        'notifications': notifications,
        'notif_count': notif_count,
    })


@login_required
@rol_requerido('madre_comunitaria')
def asistencia_estadisticas_pdf(request):
    """Genera un PDF con las mismas estadísticas (versión para descarga)."""
    madre_profile = request.user.madre_profile
    hogar_madre = HogarComunitario.objects.filter(madre=madre_profile).first()
    ninos = Nino.objects.filter(hogar=hogar_madre)

    hoy = date.today()
    hace_30_dias = hoy - timedelta(days=30)
    hace_7_dias = hoy - timedelta(days=7)

    asistencias_30 = Asistencia.objects.filter(nino__hogar=hogar_madre, fecha__gte=hace_30_dias)
    presentes_30 = asistencias_30.filter(estado="Presente").count()
    ausentes_30 = asistencias_30.filter(estado="Ausente").count()
    justificados_30 = asistencias_30.filter(estado="Justificado").count()
    total_registros_30 = asistencias_30.count()

    asistencias_7 = asistencias_30.filter(fecha__gte=hace_7_dias)
    presentes_7 = asistencias_7.filter(estado="Presente").count()
    ausentes_7 = asistencias_7.filter(estado="Ausente").count()
    justificados_7 = asistencias_7.filter(estado="Justificado").count()

    porcentaje_presentes_30 = round((presentes_30 / total_registros_30 * 100)) if total_registros_30 > 0 else 0
    porcentaje_ausentes_30 = round((ausentes_30 / total_registros_30 * 100)) if total_registros_30 > 0 else 0
    porcentaje_justificados_30 = round((justificados_30 / total_registros_30 * 100)) if total_registros_30 > 0 else 0

    estadisticas_nino = []
    for nino in ninos:
        asist_nino = Asistencia.objects.filter(nino=nino, fecha__gte=hace_30_dias)
        pres = asist_nino.filter(estado="Presente").count()
        aus = asist_nino.filter(estado="Ausente").count()
        just = asist_nino.filter(estado="Justificado").count()
        total = asist_nino.count()
        porc = round((pres / total * 100)) if total > 0 else 0

        estadisticas_nino.append({
            'nino': nino,
            'presentes': pres,
            'ausentes': aus,
            'justificados': just,
            'total': total,
            'porcentaje': porc,
        })

    context = {
        'hogar': hogar_madre,
        'presentes_30': presentes_30,
        'ausentes_30': ausentes_30,
        'justificados_30': justificados_30,
        'total_registros_30': total_registros_30,
        'porcentaje_presentes_30': porcentaje_presentes_30,
        'porcentaje_ausentes_30': porcentaje_ausentes_30,
        'porcentaje_justificados_30': porcentaje_justificados_30,
        'presentes_7': presentes_7,
        'ausentes_7': ausentes_7,
        'justificados_7': justificados_7,
        'estadisticas_nino': estadisticas_nino,
    }

    template = get_template('asistencia/estadisticas_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="estadisticas_{hogar_madre.nombre_hogar}.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response