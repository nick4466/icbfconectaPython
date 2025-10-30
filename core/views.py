from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.hashers import make_password
from .models import Usuario, Rol, Padre, Nino, HogarComunitario # Asegúrate de que todas están aquí
from django.utils import timezone

# -----------------------------------------------------------------
# 💡 NUEVA FUNCIÓN: Matricular Niño (CRUD Crear)
# -----------------------------------------------------------------

@login_required
def matricular_nino(request):
    # 1. Seguridad: Asegurar que solo las Madres Comunitarias accedan
    if request.user.rol.nombre_rol != 'madre_comunitaria':
        return redirect('role_redirect') # Redirige a donde deba ir

    # Obtener el Hogar de la Madre logueada
    # Asume que ya existe la relación: HogarComunitario.madre apunta a request.user
    # Si una madre tiene varios hogares, esto debería ser más complejo (elegir uno).
    # Por simplicidad, asumimos que tiene UNO o es el primero que encuentre.
    try:
        hogar_madre = HogarComunitario.objects.get(madre=request.user)
    except HogarComunitario.DoesNotExist:
        # Manejar el caso si a la madre no se le ha asignado un hogar
        return render(request, 'madre/error_hogar.html', {'mensaje': 'No tienes un hogar asignado.'})


    # 2. Manejar la solicitud POST (Creación de Padre y Niño)
    if request.method == 'POST':
        # Datos del formulario
        # Campos del Padre (Usuario)
        doc_padre = request.POST.get('doc_padre')
        nombres_padre = request.POST.get('nombres_padre')
        apellidos_padre = request.POST.get('apellidos_padre')
        correo_padre = request.POST.get('correo_padre')
        
        # Campos del Padre (Perfil Padre)
        ocupacion = request.POST.get('ocupacion')
        
        # Campos del Niño
        nombres_nino = request.POST.get('nombres_nino')
        apellidos_nino = request.POST.get('apellidos_nino')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        doc_nino = request.POST.get('doc_nino')
        genero_nino = request.POST.get('genero_nino')
        
        # Validación básica (deberías añadir más)
        if not all([doc_padre, nombres_padre, correo_padre, nombres_nino, fecha_nacimiento]):
            # Vuelve a mostrar el formulario con mensaje de error
            return render(request, 'madre/nino_form.html', {'error': 'Faltan campos obligatorios'})


        try:
            with transaction.atomic():
                # --- PASO A: Crear el Usuario del Padre ---
                rol_padre = Rol.objects.get(nombre_rol='padre')
                
                # La contraseña y el username serán el DOCUMENTO del padre
                password_padre = make_password(doc_padre) 
                
                usuario_padre = Usuario.objects.create(
                    username=doc_padre, # ID/Documento para login
                    password=password_padre, # Contraseña (hash del documento)
                    rol=rol_padre,
                    documento=doc_padre,
                    nombres=nombres_padre,
                    apellidos=apellidos_padre,
                    correo=correo_padre,
                    # Campos de AbstractUser por compatibilidad
                    first_name=nombres_padre, 
                    last_name=apellidos_padre,
                )

                # --- PASO B: Crear el Perfil Padre ---
                perfil_padre = Padre.objects.create(
                    usuario=usuario_padre,
                    ocupacion=ocupacion,
                    # ... puedes añadir más campos aquí ...
                )
                
                # --- PASO C: Crear el Niño ---
                Nino.objects.create(
                    nombres=nombres_nino,
                    apellidos=apellidos_nino,
                    fecha_nacimiento=fecha_nacimiento,
                    documento=doc_nino if doc_nino else None,
                    genero=genero_nino,
                    # El niño se asigna al hogar de la madre logueada
                    hogar=hogar_madre, 
                    # El niño se asigna al perfil de padre que acabamos de crear
                    padre=perfil_padre,
                    fecha_ingreso=timezone.now().date(),
                )
            
            # Si todo salió bien
            return redirect('listar_ninos') # Debes crear esta URL/vista
        
        except Rol.DoesNotExist:
            return render(request, 'madre/nino_form.html', {'error': 'El rol "padre" no existe en la base de datos.'})
        except Exception as e:
            # Manejar cualquier otro error de la base de datos
            return render(request, 'madre/nino_form.html', {'error': f'Error al matricular: {e}'})


    # 3. Manejar la solicitud GET (Mostrar el formulario)
    return render(request, 'madre/nino_form.html', {'hogar_madre': hogar_madre})


def home(request):
    return render(request, 'home.html')
@login_required
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Usuario, HogarComunitario, Rol
from django import forms

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

from core.models import Rol
from django.contrib.auth.decorators import login_required

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


from django.contrib.auth.hashers import make_password
from core.models import Usuario, Rol

@login_required
def listar_administradores(request):
    rol_admin, _ = Rol.objects.get_or_create(nombre_rol='administrador')
    administradores = Usuario.objects.filter(rol=rol_admin)
    return render(request, 'admin/administradores_list.html', {'administradores': administradores})

from django.contrib.auth.hashers import make_password
from .models import Usuario, Rol # Asegúrate de que las importaciones sean correctas

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
# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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