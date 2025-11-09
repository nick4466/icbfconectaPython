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
from django.contrib.auth.forms import SetPasswordForm
from .forms import AdminPerfilForm, MadrePerfilForm, PadrePerfilForm, NinoForm, PadreForm, CustomAuthForm

# -----------------------------------------------------------------
# 💡 NUEVA FUNCIÓN: Matricular Niño (CRUD Crear)
# -----------------------------------------------------------------

@login_required
def matricular_nino(request):
    # Solo madres comunitarias pueden acceder
    if not hasattr(request.user, 'rol') or request.user.rol.nombre_rol != 'madre_comunitaria':
        messages.error(request, 'Solo las madres comunitarias pueden matricular niños.')
        return redirect('home')

    # Obtener el hogar de la madre logueada
    try:
        hogar_madre = HogarComunitario.objects.get(madre=request.user)
    except HogarComunitario.DoesNotExist:
        messages.error(request, 'No tienes un hogar comunitario asignado.')
        return redirect('madre_dashboard')

    if request.method == 'POST':
        padre_form = PadreForm(request.POST, prefix='padre')
        nino_form = NinoForm(request.POST, prefix='nino')
        if padre_form.is_valid() and nino_form.is_valid():
            with transaction.atomic():
                # Buscar el rol padre
                rol_padre = Rol.objects.get(nombre_rol='padre')
                doc_padre = padre_form.cleaned_data['documento']
                email_padre = padre_form.cleaned_data['email']
                # Buscar usuario padre existente por documento y rol=padre
                usuario_padre = Usuario.objects.filter(documento=doc_padre, rol=rol_padre).first()
                if not usuario_padre:
                    # Si no existe, crear usuario padre
                    usuario_padre = Usuario.objects.create(
                        documento=doc_padre,
                        nombres=padre_form.cleaned_data['nombres'],
                        apellidos=padre_form.cleaned_data['apellidos'],
                        email=email_padre,
                        telefono=padre_form.cleaned_data['telefono'],
                        direccion=padre_form.cleaned_data['direccion'],
                        rol=rol_padre,
                        username=str(doc_padre),
                    )
                    # Contraseña inicial igual al documento
                    usuario_padre.set_password(str(doc_padre))
                    usuario_padre.save()
                # Crear perfil de padre si no existe
                padre_obj, created = Padre.objects.get_or_create(usuario=usuario_padre)
                padre_obj.ocupacion = padre_form.cleaned_data.get('ocupacion', '')
                padre_obj.save()
                # Crear el niño y asociar
                nino = nino_form.save(commit=False)
                nino.hogar = hogar_madre
                nino.padre = padre_obj
                nino.save()
                messages.success(request, 'Niño matriculado correctamente.')
                return redirect('listar_ninos')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        padre_form = PadreForm(prefix='padre')
        nino_form = NinoForm(prefix='nino')

    return render(request, 'madre/nino_form.html', {
        'hogar_madre': hogar_madre,
        'nino_form': nino_form,
        'padre_form': padre_form,
        'modo_edicion': False
    })
def home(request):
    return render(request, 'home.html')
@login_required
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')

# ---------- Formularios simples ----------
class MadreForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'documento', 'email', 'telefono', 'direccion']


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
            madre.username = madre.email  # obligatorio por AbstractUser
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
        email = request.POST.get('correo') # El input del form se llama 'correo'
        contraseña_plana = request.POST.get('contraseña')
        
        # 2. **CORRECCIÓN CLAVE: Mapear y crear el objeto**
        
        # OBLIGATORIO: AbstractUser requiere 'username'. Usamos el documento.
        username_val = documento
        
        # 💡 CORRECCIÓN: Validar que el documento y el correo no existan
        if Usuario.objects.filter(Q(documento=documento) | Q(email=email)).exists():
            # Si ya existe, enviar un mensaje de error y renderizar el formulario de nuevo
            # con los datos que el usuario ya había ingresado.
            messages.error(request, 'Ya existe un usuario con ese documento o correo electrónico.')
            return render(request, 'admin/administradores_form.html', {
                'admin': request.POST, # Pasamos los datos del POST para rellenar el form
                'error': True # Una bandera para el template si se necesita
            })


        if nombre and documento and email and contraseña_plana:
            Usuario.objects.create(
                # Campo obligatorio de AbstractUser
                username=username_val, 
                documento=documento,
                email=email,
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
        email = request.POST.get('correo')

        # 💡 CORRECCIÓN: Validar duplicados, excluyendo al usuario actual.
        if Usuario.objects.filter(Q(documento=documento) | Q(email=email)).exclude(id=id).exists():
            messages.error(request, 'Ya existe otro usuario con ese documento o correo electrónico.')
            # Para no perder los datos, creamos un objeto temporal con los datos del POST
            # y lo pasamos a la plantilla.
            admin_post_data = admin # Mantenemos los datos originales
            admin_post_data.nombres = request.POST.get('nombre')
            admin_post_data.documento = documento
            admin_post_data.email = email
            return render(request, 'admin/administradores_form.html', {'admin': admin_post_data})

        # Actualizar los campos del modelo a partir de los datos del POST.
        admin.nombres = request.POST.get('nombre', admin.nombres)
        admin.documento = documento
        admin.email = email
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
    # Solo madres comunitarias pueden ver su listado
    if not hasattr(request.user, 'rol') or request.user.rol.nombre_rol != 'madre_comunitaria':
        messages.error(request, 'Acceso denegado.')
        return redirect('home')
    try:
        hogar = HogarComunitario.objects.get(madre=request.user)
    except HogarComunitario.DoesNotExist:
        messages.error(request, 'No tienes un hogar comunitario asignado.')
        return redirect('madre_dashboard')
    ninos = Nino.objects.filter(hogar=hogar)
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
    # Asegurarse de que el padre y su usuario existan
    usuario_padre = nino.padre.usuario if nino.padre else None
    perfil_padre = nino.padre if nino.padre else None
    if request.method == 'POST':
        # Se instancian los formularios con los datos del POST y las instancias de los modelos
        nino_form = NinoForm(request.POST, instance=nino, prefix='nino')
        padre_form = PadreForm(request.POST, instance=usuario_padre, prefix='padre')

        if nino_form.is_valid() and padre_form.is_valid():
            # 💡 VALIDACIÓN: Verificar si el nuevo documento o correo ya existen en otro usuario.
            documento = padre_form.cleaned_data.get('documento')
            email = padre_form.cleaned_data.get('email')
            
            if Usuario.objects.filter(Q(documento=documento) | Q(email=email)).exclude(id=usuario_padre.id).exists():
                messages.error(request, 'El documento o correo electrónico ingresado ya pertenece a otro usuario.')
            else:
                # Si no hay duplicados, proceder a guardar.
                nino_form.save()
                # Guardar datos del Usuario y del perfil Padre
                usuario_actualizado = padre_form.save(commit=False)
                usuario_actualizado.save()

                if perfil_padre:
                    perfil_padre.ocupacion = padre_form.cleaned_data['ocupacion']
                    perfil_padre.save()

                messages.success(request, '¡La información del niño y su tutor ha sido actualizada!')
                return redirect('listar_ninos')

        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')

    else:
        # Se instancian los formularios con los datos existentes para el método GET.
        nino_form = NinoForm(instance=nino, prefix='nino')

        # 💡 CORRECCIÓN: Pre-llenar el formulario del padre con los datos del usuario y del perfil.
        # Los datos del modelo Usuario se cargan con 'instance'.
        # Los datos del modelo Padre (como 'ocupacion') se cargan con 'initial'.
        initial_data_padre = {
            'documento': usuario_padre.documento if usuario_padre else ''
        }
        if perfil_padre:
            initial_data_padre['ocupacion'] = perfil_padre.ocupacion
        
        padre_form = PadreForm(instance=usuario_padre, prefix='padre', initial=initial_data_padre)

    return render(request, 'madre/nino_form.html', {
        'nino_form': nino_form,
        'padre_form': padre_form,
        'nino': nino, # Se pasa el objeto nino para acceder a datos no editables en la plantilla
        'modo_edicion': True,
        'titulo_form': 'Editar Información del Niño'
    })


@login_required
def editar_perfil(request):
    user = request.user
    rol = user.rol.nombre_rol

    # 1. Seleccionar el formulario y la instancia adecuados según el rol
    if rol == 'padre':
        # Para el padre, necesitamos la instancia de su perfil de Padre
        padre_profile, _ = Padre.objects.get_or_create(usuario=user)
        FormClass = PadrePerfilForm
        initial_data = {'ocupacion': padre_profile.ocupacion, 'estrato': padre_profile.estrato}
    elif rol == 'madre_comunitaria':
        FormClass = MadrePerfilForm
        initial_data = None
    else: # administrador
        FormClass = AdminPerfilForm
        initial_data = None

    if request.method == 'POST':
        form = FormClass(request.POST, instance=user, initial=initial_data)
        if form.is_valid():
            # Guardar los datos del modelo Usuario
            user_instance = form.save(commit=False)
            # Si es un padre, guardar los campos adicionales en el modelo Padre
            if rol == 'padre':
                padre_profile.ocupacion = form.cleaned_data.get('ocupacion')
                padre_profile.estrato = form.cleaned_data.get('estrato')
                padre_profile.save()
            user_instance.save()
            messages.success(request, '¡Tu información ha sido actualizada exitosamente!')
            return redirect('editar_perfil')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        # Al cargar la página, inicializar el formulario con los datos existentes
        form = FormClass(instance=user, initial=initial_data)

    return render(request, 'perfil/editar_perfil.html', {'form': form})

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

# ----------------------------------------------------
# 💡 NUEVA FUNCIÓN: Cambiar Contraseña del Usuario
# ----------------------------------------------------
@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Actualizar la sesión para que el usuario no sea deslogueado
            update_session_auth_hash(request, user)
            messages.success(request, '¡Tu contraseña ha sido actualizada exitosamente!')
            # Redirigir a la misma página para que el usuario vea el mensaje de éxito.
            return redirect('cambiar_contrasena')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = SetPasswordForm(request.user)
    
    return render(request, 'perfil/cambiar_contrasena.html', {'form': form})