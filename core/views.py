# core/views.py
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.db import transaction, models
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from .models import Usuario, Rol, Padre, Nino, HogarComunitario, DesarrolloNino
from django.utils import timezone
from django import forms

# -----------------------------------------------------------------
# 💡 NUEVA FUNCIÓN: Matricular Niño (CRUD Crear)
# -----------------------------------------------------------------

@login_required
def matricular_nino(request):
    # 1. Seguridad: Asegurar que solo las Madres Comunitarias accedan
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    # Obtener el Hogar de la Madre logueada
    try:
        hogar_madre = HogarComunitario.objects.get(madre=request.user)
    except HogarComunitario.DoesNotExist:
        return render(request, 'madre/nino_form.html', {'error': 'No tienes un hogar asignado. Contacta al administrador.'})


    # 2. Manejar la solicitud POST (Creación de Padre y Niño)
    if request.method == 'POST':
        # Datos del formulario
        doc_padre = request.POST.get('doc_padre')
        nombres_padre = request.POST.get('nombres_padre')
        apellidos_padre = request.POST.get('apellidos_padre')
        correo_padre = request.POST.get('correo_padre')
        ocupacion = request.POST.get('ocupacion')
        nombres_nino = request.POST.get('nombres_nino')
        apellidos_nino = request.POST.get('apellidos_nino')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        doc_nino = request.POST.get('doc_nino')
        genero_nino = request.POST.get('genero_nino')
        
        if not all([doc_padre, nombres_padre, correo_padre, nombres_nino, fecha_nacimiento]):
            return render(request, 'madre/nino_form.html', {'error': 'Faltan campos obligatorios', 'hogar_madre': hogar_madre})


        try:
            with transaction.atomic():
                # 💡 CORRECCIÓN DEL ERROR: Usar get_or_create para rol 'padre' 💡
                rol_padre, created = Rol.objects.get_or_create(
                    nombre_rol='padre', 
                    defaults={'nombre_rol': 'padre'}
                )
                
                # 💡 CAMBIO: Usar get_or_create para el Usuario del padre
                # Si el usuario ya existe por su 'username' (documento), lo obtiene.
                # Si no, lo crea con los valores en 'defaults'.
                usuario_padre, usuario_creado = Usuario.objects.get_or_create(
                    username=doc_padre,
                    defaults={
                        'password': make_password(doc_padre), 
                        'rol': rol_padre,
                        'documento': doc_padre,
                        'nombres': nombres_padre,
                        'apellidos': apellidos_padre,
                        'correo': correo_padre,
                        'first_name': nombres_padre, 
                        'last_name': apellidos_padre,
                    }
                )

                # 💡 CAMBIO: Usar get_or_create para el Perfil del padre
                # Esto asegura que cada usuario padre tenga solo un perfil de padre.
                perfil_padre, perfil_creado = Padre.objects.get_or_create(
                    usuario=usuario_padre,
                    defaults={'ocupacion': ocupacion}
                )
                
                # Crear el Niño
                Nino.objects.create(
                    nombres=nombres_nino,
                    apellidos=apellidos_nino,
                    fecha_nacimiento=fecha_nacimiento,
                    documento=doc_nino if doc_nino else None,
                    genero=genero_nino,
                    hogar=hogar_madre, 
                    padre=perfil_padre,
                    fecha_ingreso=timezone.now().date(),
                )
            
            return redirect('listar_ninos')
        
        except Exception as e:
            # Maneja errores de unicidad (documento/correo duplicado) o DB
            return render(request, 'madre/nino_form.html', {'error': f'Error al matricular: {e}', 'hogar_madre': hogar_madre})


    # 3. Manejar la solicitud GET (Mostrar el formulario)
    return render(request, 'madre/nino_form.html', {'hogar_madre': hogar_madre})
def home(request):
    return render(request, 'home.html')
@login_required
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')

# ---------- Formularios simples ----------
class MadreForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'documento', 'correo', 'telefono', 'direccion']

class HogarForm(forms.ModelForm):
    class Meta:
        model = HogarComunitario
        fields = ['nombre_hogar', 'direccion', 'localidad', 'estado']
# En la sección de formularios simples en views.py
class AdministradorForm(forms.ModelForm):
    # Añadir el campo de contraseña, ya que no se incluye automáticamente
    contraseña = forms.CharField(widget=forms.PasswordInput, required=True)
    
    class Meta:
        model = Usuario
        # Elige los campos que quieres:
        fields = ['first_name', 'email', 'rol'] # Asumiendo estos nombres para Usuario

# ---------- CRUD MADRES ----------
@login_required
def listar_madres(request):
    madres = Usuario.objects.filter(rol__nombre_rol='madre_comunitaria').prefetch_related('hogares_asignados')
    return render(request, 'admin/madres_list.html', {'madres': madres})

@login_required
def listar_hogares(request):
    # Selecciona los hogares y la madre asociada para optimizar la consulta
    # 💡 MEJORA: Anotar cada hogar con el número de niños matriculados
    hogares = HogarComunitario.objects.select_related('madre').annotate(num_ninos=models.Count('ninos')).all()
    return render(request, 'admin/hogares_list.html', {'hogares': hogares})

@login_required
def crear_madre(request):
    rol_madre, _ = Rol.objects.get_or_create(nombre_rol='madre_comunitaria')
    
    if request.method == 'POST':
        madre_form = MadreForm(request.POST, prefix='madre')
        hogar_form = HogarForm(request.POST, prefix='hogar')

        if madre_form.is_valid() and hogar_form.is_valid():
            # Validación para hogar duplicado
            nombre_hogar = hogar_form.cleaned_data['nombre_hogar']
            direccion_hogar = hogar_form.cleaned_data['direccion']
            localidad = hogar_form.cleaned_data['localidad']

            if HogarComunitario.objects.filter(nombre_hogar__iexact=nombre_hogar, localidad__iexact=localidad).exists():
                messages.error(request, f"Ya existe un hogar llamado '{nombre_hogar}' en la localidad de '{localidad}'.")
            elif HogarComunitario.objects.filter(direccion__iexact=direccion_hogar).exists():
                messages.error(request, f"La dirección '{direccion_hogar}' ya está registrada para otro hogar.")
            
            # Si hay mensajes de error, renderizar de nuevo el formulario
            if messages.get_messages(request):
                 return render(request, 'admin/madres_form.html', {
                    'madre_form': madre_form,
                    'hogar_form': hogar_form
                })
            madre = madre_form.save(commit=False)
            madre.rol = rol_madre
            madre.username = madre.correo  # obligatorio por AbstractUser
            madre.set_password('123456')   # contraseña por defecto
            madre.save()

            hogar = hogar_form.save(commit=False)
            hogar.madre = madre
            hogar.save()
            
            messages.success(request, '¡Madre comunitaria y hogar creados exitosamente!')
            return redirect('listar_madres')
    else:
        madre_form = MadreForm(prefix='madre')
        hogar_form = HogarForm(prefix='hogar')

    return render(request, 'admin/madres_form.html', {
        'madre_form': madre_form,
        'hogar_form': hogar_form
    })


@login_required
def editar_madre(request, id):
    madre = get_object_or_404(Usuario, id=id, rol__nombre_rol='madre_comunitaria')
    hogar = HogarComunitario.objects.filter(madre=madre).first()

    if request.method == 'POST':
        madre_form = MadreForm(request.POST, instance=madre, prefix='madre')
        hogar_form = HogarForm(request.POST, instance=hogar, prefix='hogar')
        if madre_form.is_valid() and hogar_form.is_valid():
            # Validación para hogar duplicado, excluyendo el hogar actual
            nombre_hogar = hogar_form.cleaned_data['nombre_hogar']
            direccion_hogar = hogar_form.cleaned_data['direccion']
            localidad = hogar_form.cleaned_data['localidad']

            if HogarComunitario.objects.filter(nombre_hogar__iexact=nombre_hogar, localidad__iexact=localidad).exclude(id=hogar.id).exists():
                messages.error(request, f"Ya existe otro hogar llamado '{nombre_hogar}' en la localidad de '{localidad}'.")
            elif HogarComunitario.objects.filter(direccion__iexact=direccion_hogar).exclude(id=hogar.id).exists():
                messages.error(request, f"La dirección '{direccion_hogar}' ya está registrada para otro hogar.")

            # Si hay mensajes de error, renderizar de nuevo el formulario
            if messages.get_messages(request):
                 return render(request, 'admin/madres_form.html', {
                    'madre_form': madre_form,
                    'hogar_form': hogar_form
                })

            madre_form.save()
            hogar_form.save()
            messages.success(request, '¡Madre comunitaria actualizada exitosamente!')
            return redirect('listar_madres')
    else:
        madre_form = MadreForm(instance=madre, prefix='madre')
        hogar_form = HogarForm(instance=hogar, prefix='hogar')

    return render(request, 'admin/madres_form.html', {
        'madre_form': madre_form,
        'hogar_form': hogar_form
    })


@login_required
def eliminar_madre(request, id):
    madre = get_object_or_404(Usuario, id=id, rol__nombre_rol='madre_comunitaria')
    madre.delete()
    messages.success(request, '¡Madre comunitaria eliminada exitosamente!')
    return redirect('listar_madres')

@login_required
def listar_administradores(request):
    rol_admin, _ = Rol.objects.get_or_create(nombre_rol='administrador')
    # Ordenar por nombre para una mejor visualización
    administradores = Usuario.objects.filter(rol=rol_admin).order_by('nombres')
    return render(request, 'admin/administradores_list.html', {'administradores': administradores})


@login_required
def crear_administrador(request):
    rol_admin, _ = Rol.objects.get_or_create(nombre_rol='administrador')
    
    if request.method == 'POST':
        # 1. Obtener los datos del formulario (usando .get() es más seguro)
        nombre = request.POST.get('nombre')
        documento = request.POST.get('documento')
        correo = request.POST.get('correo')
        contraseña_plana = request.POST.get('contraseña')
        
        # 2. **CORRECCIÓN CLAVE: Mapear y crear el objeto**
        
        # OBLIGATORIO: AbstractUser requiere 'username'. Usamos el documento.
        username_val = documento
        
        # 💡 CORRECCIÓN: Validar que el documento y el correo no existan
        if Usuario.objects.filter(Q(documento=documento) | Q(correo=correo)).exists():
            # Si ya existe, enviar un mensaje de error y renderizar el formulario de nuevo
            # con los datos que el usuario ya había ingresado.
            messages.error(request, 'Ya existe un usuario con ese documento o correo electrónico.')
            return render(request, 'admin/administradores_form.html', {
                'admin': request.POST, # Pasamos los datos del POST para rellenar el form
                'error': True # Una bandera para el template si se necesita
            })


        if nombre and documento and correo and contraseña_plana:
            Usuario.objects.create(
                # Campo obligatorio de AbstractUser
                username=username_val, 
                documento=documento,
                correo=correo,
                nombres=nombre,
                apellidos="", # Lo dejas vacío ya que el form no lo pide
                # Campo de AbstractUser (donde se guarda el hash)
                password=make_password(contraseña_plana),
                rol=rol_admin
            )
            
            # 💡 CORRECCIÓN: Añadir mensaje de éxito y redirigir a la lista.
            messages.success(request, '¡Administrador creado exitosamente!')
            return redirect('listar_administradores')
            
    return render(request, 'admin/administradores_form.html', {'admin': None})
@login_required
def editar_administrador(request, id):
    # Usar get_object_or_404 es una mejor práctica para obtener objetos.
    admin = get_object_or_404(Usuario, id=id, rol__nombre_rol='administrador')
    
    if request.method == 'POST':
        documento = request.POST.get('documento')
        correo = request.POST.get('correo')

        # 💡 CORRECCIÓN: Validar duplicados, excluyendo al usuario actual.
        if Usuario.objects.filter(Q(documento=documento) | Q(correo=correo)).exclude(id=id).exists():
            messages.error(request, 'Ya existe otro usuario con ese documento o correo electrónico.')
            # Para no perder los datos, creamos un objeto temporal con los datos del POST
            # y lo pasamos a la plantilla.
            admin_post_data = admin # Mantenemos los datos originales
            admin_post_data.nombres = request.POST.get('nombre')
            admin_post_data.documento = documento
            admin_post_data.correo = correo
            return render(request, 'admin/administradores_form.html', {'admin': admin_post_data})

        # Actualizar los campos del modelo a partir de los datos del POST.
        admin.nombres = request.POST.get('nombre', admin.nombres)
        admin.documento = documento
        admin.correo = correo
        admin.username = documento # Sincronizar username con documento
        
        # Solo actualizar la contraseña si se proporciona una nueva.
        nueva_contraseña = request.POST.get('contraseña')
        if nueva_contraseña:
            admin.password = make_password(nueva_contraseña)
            # 💡 CORRECCIÓN: Si el admin edita su propia cuenta, actualiza la sesión para no desloguearlo.
            if request.user.id == admin.id:
                update_session_auth_hash(request, admin)

            
        admin.save()
        # 💡 CORRECCIÓN: Añadir mensaje de éxito y redirigir a la lista.
        messages.success(request, '¡Administrador actualizado exitosamente!')
        return redirect('listar_administradores')
        
    # **LA CORRECCIÓN CLAVE:** Apuntar a la ruta correcta de la plantilla.
    return render(request, 'admin/administradores_form.html', {'admin': admin})

@login_required
def eliminar_administrador(request, id):
    Usuario.objects.filter(id=id).delete()
    return redirect('listar_administradores')
# ... Tus otras funciones (home, admin_dashboard, crear_madre, etc.) ...

# ----------------------------------------------------
# 💡 NUEVA FUNCIÓN: Redirección por Rol (Se ejecuta después del login)
# ----------------------------------------------------
@login_required
def role_redirect(request):
    """
    Redirige al dashboard apropiado según el rol del usuario.
    Esta será la URL de redirección principal después de un login exitoso.
    """
    # 💡 CORRECCIÓN: Verificar si el usuario tiene un rol asignado
    if not request.user.rol:
        # Si no tiene rol (ej. superusuario sin rol asignado), redirigir a home
        # o a una página de "acceso denegado".
        return redirect('home')

    # El campo 'rol' es una ForeignKey, accedemos al nombre con '.nombre_rol'
    role = request.user.rol.nombre_rol

    if role == 'administrador':
        # Redirige a la URL con name='admin_dashboard'
        return redirect('admin_dashboard')

    elif role == 'madre_comunitaria':
        # Redirige a la URL que crearemos: name='madre_dashboard'
        return redirect('madre_dashboard')
    
    elif role == 'padre':
        # Redirige al dashboard del padre
        return redirect('padre_dashboard')

    # Si el rol es 'padre' o no está definido, puede redirigir al home
    return redirect('home')


# ----------------------------------------------------
# 💡 NUEVA FUNCIÓN: Dashboard de la Madre Comunitaria
# ----------------------------------------------------
@login_required
def madre_dashboard(request):
    # Verificación de seguridad adicional
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect') # O a una página de acceso denegado

    # Aquí cargarías datos específicos de la madre (niños asignados, asistencia, etc.)
    hogar_madre = HogarComunitario.objects.filter(madre=request.user).first()
    return render(request, 'madre/dashboard.html', {'hogar_madre': hogar_madre})


# ----------------------------------------------------
# 💡 NUEVA FUNCIÓN: Dashboard del Padre de Familia
# ----------------------------------------------------
@login_required
def padre_dashboard(request):
    if request.user.rol.nombre_rol != 'padre':
        return redirect('role_redirect')

    try:
        # Encontrar el perfil del padre y luego a su hijo
        padre = Padre.objects.get(usuario=request.user)
        # 💡 CAMBIO: Obtener TODOS los niños asociados al padre
        ninos_qs = Nino.objects.filter(padre=padre).order_by('nombres')

        # 💡 MEJORA: Añadir el último desarrollo a cada niño para mostrarlo en el dashboard
        ninos_con_desarrollo = []
        for nino in ninos_qs:
            ultimo_desarrollo = DesarrolloNino.objects.filter(nino=nino).order_by('-fecha_fin_mes').first()
            ninos_con_desarrollo.append({
                'nino': nino,
                'ultimo_desarrollo': ultimo_desarrollo
            })

        return render(request, 'padre/dashboard.html', {
            'ninos_data': ninos_con_desarrollo,
        })
    except Padre.DoesNotExist:
        # Manejar el caso donde el padre no tiene un hijo asignado
        return render(request, 'padre/dashboard.html', {'error': 'No tienes un niño asignado.'})


# ----------------------------------------------------
# 💡 NUEVA FUNCIÓN: Ver Desarrollo (Vista del Padre)
# ----------------------------------------------------
@login_required
def padre_ver_desarrollo(request, nino_id):
    if request.user.rol.nombre_rol != 'padre':
        return redirect('role_redirect')

    try:
        padre = Padre.objects.get(usuario=request.user)
        # 💡 CAMBIO: Obtener el niño específico y verificar que pertenece al padre
        nino = get_object_or_404(Nino, id=nino_id, padre=padre)
        
        desarrollos = []
        if nino:
            desarrollos = DesarrolloNino.objects.filter(nino=nino).order_by('-fecha_fin_mes')

        return render(request, 'padre/desarrollo_list.html', {'nino': nino, 'desarrollos': desarrollos})
    except (Padre.DoesNotExist, Nino.DoesNotExist):
        return redirect('padre_dashboard')

# core/views.py

# ... (tus otras funciones) ...

@login_required
def listar_ninos(request):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    # Filtra los hogares que son gestionados por la madre logueada
    # Esto asume que HogarComunitario.madre es el usuario logueado
    hogares_madre = HogarComunitario.objects.filter(madre=request.user)
    
    # Filtra los niños que pertenecen a esos hogares
    ninos = Nino.objects.filter(hogar__in=hogares_madre).order_by('apellidos')

    return render(request, 'madre/nino_list.html', {'ninos': ninos})

# -----------------------------------------------------------------
# 💡 NUEVA FUNCIÓN: Registrar Desarrollo del Niño (CRUD Crear/Actualizar)
# -----------------------------------------------------------------
@login_required
def registrar_desarrollo(request):
    # Esta vista ahora solo maneja la creación
    nino_id_preseleccionado = request.GET.get('nino')

    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    try:
        hogar_madre = HogarComunitario.objects.get(madre=request.user)
    except HogarComunitario.DoesNotExist:
        return redirect('madre_dashboard')

    ninos_del_hogar = Nino.objects.filter(hogar=hogar_madre)

    if request.method == 'POST':
        nino_id = request.POST.get('nino')
        fecha_registro = request.POST.get('fecha_registro')
        cognitiva = request.POST.get('dimension_cognitiva')
        comunicativa = request.POST.get('dimension_comunicativa')
        socio_afectiva = request.POST.get('dimension_socio_afectiva')
        corporal = request.POST.get('dimension_corporal')
        
        if not all([nino_id, fecha_registro, cognitiva, comunicativa, socio_afectiva, corporal]):
            return render(request, 'madre/desarrollo_form.html', {
                'ninos': ninos_del_hogar,
                'error': 'Todos los campos son obligatorios.'
            })

        DesarrolloNino.objects.create(
            nino_id=nino_id,
            fecha_fin_mes=fecha_registro,
            dimension_cognitiva=cognitiva,
            dimension_comunicativa=comunicativa,
            dimension_socio_afectiva=socio_afectiva,
            dimension_corporal=corporal,
        )
        
        # Redirigir con el filtro del niño y un mensaje de éxito
        redirect_url = reverse('listar_desarrollos')
        return redirect(f'{redirect_url}?nino={nino_id}&exito=1')

    return render(request, 'madre/desarrollo_form.html', {
        'ninos': ninos_del_hogar,
        'form_action': reverse('registrar_desarrollo'),
        'titulo_form': 'Registrar Desarrollo de Niño',
        'nino_id_preseleccionado': nino_id_preseleccionado,
    })

# -----------------------------------------------------------------
# 💡 NUEVA FUNCIÓN: Listar Registros de Desarrollo (CRUD Leer)
# -----------------------------------------------------------------
@login_required
def listar_desarrollos(request):
    # 1. Seguridad y obtener el hogar de la madre
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')
    
    try:
        hogar_madre = HogarComunitario.objects.get(madre=request.user)
    except HogarComunitario.DoesNotExist:
        return render(request, 'madre/desarrollo_list.html', {'error': 'No tienes un hogar asignado.'})

    # 2. Obtener la lista base de desarrollos y niños para los filtros
    desarrollos = DesarrolloNino.objects.filter(nino__hogar=hogar_madre).select_related('nino', 'nino__padre__usuario').order_by('-fecha_fin_mes')
    ninos_del_hogar = Nino.objects.filter(hogar=hogar_madre)

    # 3. Aplicar filtros si existen
    nino_id_filtro = request.GET.get('nino')
    mes_filtro = request.GET.get('mes') # Formato YYYY-MM

    if nino_id_filtro:
        desarrollos = desarrollos.filter(nino__id=nino_id_filtro)
    
    if mes_filtro:
        # Filtra por año y mes de la fecha de fin de mes
        year, month = map(int, mes_filtro.split('-'))
        desarrollos = desarrollos.filter(fecha_fin_mes__year=year, fecha_fin_mes__month=month)

    # 4. Renderizar la plantilla con el contexto
    return render(request, 'madre/desarrollo_list.html', {
        'desarrollos': desarrollos,
        'ninos': ninos_del_hogar,
        'nino_id_filtro': nino_id_filtro, # Para mantener la selección del filtro
        'mes_filtro': mes_filtro,
    })

# -----------------------------------------------------------------
# 💡 NUEVA FUNCIÓN: Editar Registro de Desarrollo (CRUD Actualizar)
# -----------------------------------------------------------------
@login_required
def editar_desarrollo(request, id):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    desarrollo = get_object_or_404(DesarrolloNino, id=id)

    if desarrollo.nino.hogar.madre != request.user:
        return redirect('listar_desarrollos')

    if request.method == 'POST':
        desarrollo.fecha_fin_mes = request.POST.get('fecha_registro')
        desarrollo.dimension_cognitiva = request.POST.get('dimension_cognitiva')
        desarrollo.dimension_comunicativa = request.POST.get('dimension_comunicativa')
        desarrollo.dimension_socio_afectiva = request.POST.get('dimension_socio_afectiva')
        desarrollo.dimension_corporal = request.POST.get('dimension_corporal')
        desarrollo.save()
        
        # Redirigir con el filtro del niño y un mensaje de éxito
        redirect_url = reverse('listar_desarrollos')
        return redirect(f'{redirect_url}?nino={desarrollo.nino.id}&exito=1')

    return render(request, 'madre/desarrollo_form.html', {
        'desarrollo': desarrollo,
        'form_action': reverse('editar_desarrollo', args=[id]),
        'titulo_form': 'Editar Registro de Desarrollo',
        'nino_id_preseleccionado': desarrollo.nino.id,
    })

# -----------------------------------------------------------------
# 💡 NUEVA FUNCIÓN: Eliminar Registro de Desarrollo (CRUD Eliminar)
# -----------------------------------------------------------------
@login_required
def eliminar_desarrollo(request, id):
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect')

    desarrollo = get_object_or_404(DesarrolloNino, id=id)

    if desarrollo.nino.hogar.madre != request.user:
        return redirect('listar_desarrollos')

    nino_id = desarrollo.nino.id
    desarrollo.delete()
    
    redirect_url = reverse('listar_desarrollos')
    return redirect(f'{redirect_url}?nino={nino_id}')

@login_required
def ver_ficha_nino(request, id):
    nino = get_object_or_404(Nino, id=id)
    return render(request, 'madre/nino_ficha.html', {'nino': nino})

@login_required
def editar_nino(request, id):
    nino = get_object_or_404(Nino, id=id)
    padre = nino.padre
    usuario_padre = padre.usuario
    if request.method == 'POST':
        # Actualizar datos del padre
        usuario_padre.nombres = request.POST.get('nombres_padre', usuario_padre.nombres)
        usuario_padre.apellidos = request.POST.get('apellidos_padre', usuario_padre.apellidos)
        usuario_padre.telefono = request.POST.get('telefono_padre', usuario_padre.telefono)
        usuario_padre.direccion = request.POST.get('direccion_padre', usuario_padre.direccion)
        usuario_padre.save()
        padre.ocupacion = request.POST.get('ocupacion', padre.ocupacion)
        padre.estrato = request.POST.get('estrato', padre.estrato)
        padre.save()
        # Actualizar datos del niño
        nino.nombres = request.POST.get('nombres_nino', nino.nombres)
        nino.apellidos = request.POST.get('apellidos_nino', nino.apellidos)
        nino.documento = request.POST.get('doc_nino', nino.documento)
        nino.fecha_nacimiento = request.POST.get('fecha_nacimiento', nino.fecha_nacimiento)
        nino.genero = request.POST.get('genero', nino.genero)
        nino.nacionalidad = request.POST.get('nacionalidad', nino.nacionalidad)
        nino.save()
        return redirect('listar_ninos')
    # Renderizar el formulario con los datos actuales
    return render(request, 'madre/nino_form.html', {
        'nino': nino,
        'padre': padre,
        'usuario_padre': usuario_padre,
        'hogar_madre': nino.hogar,
        'modo_edicion': True
    })

@login_required
def generar_reporte_ninos(request):
    # Aquí puedes generar el PDF o mostrar un mensaje temporal
    return render(request, 'madre/reporte_ninos.html')

@login_required
def eliminar_nino(request, id):
    nino = get_object_or_404(Nino, id=id)
    nino.delete()
    return redirect('listar_ninos')

@login_required
def gestion_ninos(request):
    # Ejemplo: obtener los niños del hogar de la madre logueada
    ninos = Nino.objects.all()  # Ajusta el filtro según tu lógica de negocio
    return render(request, 'madre/gestion_ninos_list.html', {'ninos': ninos})