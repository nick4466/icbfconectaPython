# core/views.py
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.hashers import make_password
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
        return render(request, 'madre/nino_form.html', {'error': 'No tienes un hogar asignado. Contacta al administrador.', 'form_action': reverse('matricular_nino')})


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
            return render(request, 'madre/nino_form.html', {'error': 'Faltan campos obligatorios', 'hogar_madre': hogar_madre, 'form_action': reverse('matricular_nino')})


        try:
            with transaction.atomic():
                # 💡 CORRECCIÓN DEL ERROR: Usar get_or_create para rol 'padre' 💡
                rol_padre, created = Rol.objects.get_or_create(
                    nombre_rol='padre', 
                    defaults={'nombre_rol': 'padre'}
                )
                
                # Crear Usuario del Padre
                password_padre = make_password(doc_padre) 
                
                usuario_padre = Usuario.objects.create(
                    username=doc_padre, 
                    password=password_padre, 
                    rol=rol_padre,
                    documento=doc_padre,
                    nombres=nombres_padre,
                    apellidos=apellidos_padre,
                    correo=correo_padre,
                    first_name=nombres_padre, 
                    last_name=apellidos_padre,
                )

                # Crear Perfil Padre
                perfil_padre = Padre.objects.create(
                    usuario=usuario_padre,
                    ocupacion=ocupacion,
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
            return render(request, 'madre/nino_form.html', {'error': f'Error al matricular: {e}', 'hogar_madre': hogar_madre, 'form_action': reverse('matricular_nino')})


    # 3. Manejar la solicitud GET (Mostrar el formulario)
    return render(request, 'madre/nino_form.html', {
        'hogar_madre': hogar_madre,
        'form_action': reverse('matricular_nino'),
        'titulo_form': 'Matricular Niño Nuevo'
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
        fields = ['nombres', 'apellidos', 'documento', 'correo', 'telefono', 'direccion']

class HogarForm(forms.ModelForm):
    class Meta:
        model = HogarComunitario
        fields = ['nombre_hogar', 'direccion', 'localidad', 'capacidad_maxima', 'estado']
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
    madres = Usuario.objects.filter(rol__nombre_rol='madre_comunitaria')
    return render(request, 'admin/madres_list.html', {'madres': madres})

@login_required
def crear_madre(request):
    rol_madre, _ = Rol.objects.get_or_create(nombre_rol='madre_comunitaria')
    
    if request.method == 'POST':
        madre_form = MadreForm(request.POST)
        hogar_form = HogarForm(request.POST)

        if madre_form.is_valid() and hogar_form.is_valid():
            madre = madre_form.save(commit=False)
            madre.rol = rol_madre
            madre.username = madre.correo  # obligatorio por AbstractUser
            madre.set_password('123456')   # contraseña por defecto
            madre.save()

            hogar = hogar_form.save(commit=False)
            hogar.madre = madre
            hogar.save()

            return redirect('listar_madres')
    else:
        madre_form = MadreForm()
        hogar_form = HogarForm()

    return render(request, 'admin/madres_form.html', {
        'madre_form': madre_form,
        'hogar_form': hogar_form
    })


@login_required
def editar_madre(request, id):
    madre = get_object_or_404(Usuario, id=id, rol__nombre_rol='madre_comunitaria')
    hogar = HogarComunitario.objects.filter(madre=madre).first()

    if request.method == 'POST':
        madre_form = MadreForm(request.POST, instance=madre)
        hogar_form = HogarForm(request.POST, instance=hogar)
        if madre_form.is_valid() and hogar_form.is_valid():
            madre_form.save()
            hogar_form.save()
            return redirect('listar_madres')
    else:
        madre_form = MadreForm(instance=madre)
        hogar_form = HogarForm(instance=hogar)

    return render(request, 'admin/madres_form.html', {
        'madre_form': madre_form,
        'hogar_form': hogar_form
    })


@login_required
def eliminar_madre(request, id):
    madre = get_object_or_404(Usuario, id=id, rol__nombre_rol='madre_comunitaria')
    madre.delete()
    return redirect('listar_madres')

@login_required
def listar_administradores(request):
    rol_admin, _ = Rol.objects.get_or_create(nombre_rol='administrador')
    administradores = Usuario.objects.filter(rol=rol_admin)
    return render(request, 'admin/administradores_list.html', {'administradores': administradores})


@login_required
def crear_administrador(request):
    rol_admin, _ = Rol.objects.get_or_create(nombre_rol='administrador')
    
    if request.method == 'POST':
        # 1. Obtener los datos del formulario (usando .get() es más seguro)
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contraseña_plana = request.POST.get('contraseña')
        
        # 2. **CORRECCIÓN CLAVE: Mapear y crear el objeto**
        
        # OBLIGATORIO: AbstractUser requiere el campo 'username'.
        # Lo más lógico es usar el 'correo' como valor para 'username' si es único.
        username_val = correo # Usamos el correo como username
        
        if nombre and correo and contraseña_plana:
            # Usamos los nombres de campos EXACTOS de tu modelo Usuario:
            Usuario.objects.create(
                # Campo obligatorio de AbstractUser
                username=username_val, 
                # Campo de tu modelo (que coincide con el formulario)
                correo=correo,
                # Campo de tu modelo
                nombres=nombre,
                # Campo de tu modelo
                apellidos="", # Lo dejas vacío ya que el form no lo pide
                # Campo de AbstractUser (donde se guarda el hash)
                password=make_password(contraseña_plana),
                rol=rol_admin
            )
            
            # 3. Redirección
            return redirect('listar_administradores')
            
    return render(request, 'admin/administradores_form.html', {'admin': None})
@login_required
def editar_administrador(request, id):
    admin = Usuario.objects.get(id=id)
    if request.method == 'POST':
        admin.nombre = request.POST['nombre']
        admin.correo = request.POST['correo']
        if request.POST.get('contraseña'):
            admin.contraseña = make_password(request.POST['contraseña'])
        admin.save()
        return redirect('listar_administradores')
    return render(request, 'administradores_form.html', {'admin': admin})

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
    return render(request, 'madre/dashboard.html') # Necesitas crear este template


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
        
        return redirect('listar_desarrollos')

    return render(request, 'madre/desarrollo_form.html', {
        'ninos': ninos_del_hogar,
        'form_action': reverse('registrar_desarrollo'),
        'titulo_form': 'Registrar Desarrollo de Niño'
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
        return redirect('listar_desarrollos')

    return render(request, 'madre/desarrollo_form.html', {
        'desarrollo': desarrollo,
        'form_action': reverse('editar_desarrollo', args=[id]),
        'titulo_form': 'Editar Registro de Desarrollo'
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

    desarrollo.delete()
    return redirect('listar_desarrollos')

@login_required
def ver_ficha_nino(request, id):
    nino = get_object_or_404(Nino, id=id)
    return render(request, 'madre/nino_ficha.html', {'nino': nino})

@login_required
def editar_nino(request, id):
    nino = get_object_or_404(Nino, id=id)
    # Seguridad: Asegurarse que la madre solo edita niños de su hogar
    if nino.hogar.madre != request.user:
        return redirect('listar_ninos')

    if request.method == 'POST':
        # Actualizar datos del padre
        nino.padre.usuario.nombres = request.POST.get('nombres_padre', nino.padre.usuario.nombres)
        nino.padre.usuario.apellidos = request.POST.get('apellidos_padre', nino.padre.usuario.apellidos)
        nino.padre.usuario.correo = request.POST.get('correo_padre', nino.padre.usuario.correo)
        nino.padre.usuario.telefono = request.POST.get('telefono_padre', nino.padre.usuario.telefono)
        nino.padre.usuario.save()

        nino.padre.ocupacion = request.POST.get('ocupacion', nino.padre.ocupacion)
        nino.padre.save()

        # Actualizar datos del niño
        nino.nombres = request.POST.get('nombres_nino', nino.nombres)
        nino.apellidos = request.POST.get('apellidos_nino', nino.apellidos)
        nino.documento = request.POST.get('doc_nino', nino.documento)
        nino.fecha_nacimiento = request.POST.get('fecha_nacimiento', nino.fecha_nacimiento)
        nino.genero = request.POST.get('genero_nino', nino.genero)
        nino.save()
        return redirect('listar_ninos')

    return render(request, 'madre/nino_form.html', {
        'nino': nino,
        'padre': nino.padre,
        'hogar_madre': nino.hogar,
        'modo_edicion': True,
        'form_action': reverse('editar_nino', args=[id]),
        'titulo_form': 'Editar Ficha del Niño',
        'texto_boton': 'Guardar Cambios'
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