from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


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

@login_required
def crear_administrador(request):
    rol_admin, _ = Rol.objects.get_or_create(nombre_rol='administrador')
    if request.method == 'POST':
        nombre = request.POST['nombre']
        correo = request.POST['correo']
        contraseña = make_password(request.POST['contraseña'])
        Usuario.objects.create(nombre=nombre, correo=correo, contraseña=contraseña, rol=rol_admin)
        return redirect('administradores_list')
    return render(request, 'admin/administradores_form.html')

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
