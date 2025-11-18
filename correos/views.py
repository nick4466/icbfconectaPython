from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage, get_connection
from django.conf import settings

from core.models import Padre
from .forms import EmailMassForm
from .models import ArchivoAdjunto, EmailLog
from django.views.decorators.http import require_POST
from django.db.models import Q
from datetime import datetime
from .models import EmailLog


def obtener_choices_padres():
    padres = Padre.objects.select_related("usuario").prefetch_related("ninos").all()
    choices = []
    for p in padres:
        correo = p.usuario.correo
        ninos = ", ".join([f"{n.nombres} {n.apellidos}" for n in p.ninos.all()])
        label = f"{correo} - {ninos}"
        choices.append((str(p.id), label))
    return choices


def enviar_correos(request):
    if request.method == "POST":
        form = EmailMassForm(request.POST, request.FILES, destinatarios_choices=obtener_choices_padres())
        if form.is_valid():
            selected_ids = form.cleaned_data['destinatarios']
            asunto = form.cleaned_data['asunto']
            cuerpo = form.cleaned_data['cuerpo']
            archivos = request.FILES.getlist('archivos')

            padres = Padre.objects.filter(id__in=selected_ids).select_related("usuario").prefetch_related("ninos")

            adjuntos_guardados = []
            for f in archivos:
                adj = ArchivoAdjunto(archivo=f, nombre_original=f.name)
                adj.save()
                adjuntos_guardados.append(adj)

            destinatarios_lista = [p.usuario.correo for p in padres]

            connection = get_connection()
            try:
                connection.open()
            except:
                pass

            fallos = []

            for p in padres:
                correo_padre = p.usuario.correo
                nombres_ninos = ", ".join([f"{n.nombres} {n.apellidos}" for n in p.ninos.all()])

                cuerpo_final = (
                    f"Hola {p.usuario.nombres},\n\n"
                    f"{cuerpo}\n\n"
                    f"Niño(s) asociado(s): {nombres_ninos}"
                )

                email = EmailMessage(
                    subject=asunto,
                    body=cuerpo_final,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[correo_padre],
                    connection=connection
                )

                for adj in adjuntos_guardados:
                    email.attach(adj.nombre_original, adj.archivo.read())

                try:
                    email.send()
                except Exception as e:
                    fallos.append(f"{correo_padre}: {str(e)}")

            log = EmailLog.objects.create(
                asunto=asunto,
                cuerpo=cuerpo,
                destinatarios=",".join(destinatarios_lista),
                enviado_con_exito=(len(fallos) == 0),
                nota_error="\n".join(fallos)
            )

            if adjuntos_guardados:
                log.adjuntos.set(adjuntos_guardados)

            messages.success(request, "Correos enviados correctamente.")
            return redirect("correos:historial")

    else:
        form = EmailMassForm(destinatarios_choices=obtener_choices_padres())

    return render(request, "correos/enviar.html", {"form": form})


def historial(request):
    logs = EmailLog.objects.all().order_by("-fecha_envio")

    # --- FILTROS ---
    mes = request.GET.get("mes")
    nombre = request.GET.get("nombre")

    # Filtrar por mes
    if mes:
        try:
            fecha = datetime.strptime(mes, "%Y-%m")
            logs = logs.filter(
                fecha_envio__year=fecha.year,
                fecha_envio__month=fecha.month
            )
        except:
            pass

    # Filtrar por nombre de destinatario (correo)
    if nombre:
        logs = logs.filter(destinatarios__icontains=nombre)

    # Lista de correos convertida en array
    for log in logs:
        log.lista_destinatarios = log.destinatarios.split(",")

    return render(request, "correos/historial.html", {
        "logs": logs
    })
@require_POST
def eliminar_log(request, log_id):
    try:
        log = EmailLog.objects.get(id=log_id)
        log.delete()
        messages.success(request, "Registro eliminado correctamente.")
    except EmailLog.DoesNotExist:
        messages.error(request, "El registro no existe.")
    return redirect("correos:historial")


@require_POST
def vaciar_historial(request):
    EmailLog.objects.all().delete()
    messages.success(request, "Historial vaciado correctamente.")
    return redirect("correos:historial")