from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import CustomUser, Proveedor
from django.db import IntegrityError
from .forms import ContactForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm

def group_required(*group_names):
    def in_groups(user):
        if user.is_authenticated:
            if user.groups.filter(name__in=group_names).exists():
                return True
        return False

    def decorator(view_func):
        @login_required(login_url='/user/login/')
        def _wrapped_view(request, *args, **kwargs):
            if in_groups(request.user):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("No tienes permiso para acceder a esta página")
        return _wrapped_view
    return decorator

def user_role_context(request):
    is_empleado = False
    is_cliente = False

    if request.user.is_authenticated:
        is_empleado = request.user.groups.filter(name='Empleados').exists()
        is_cliente = request.user.groups.filter(name='Clientes').exists()

    return {
        'is_empleado': is_empleado,
        'is_cliente': is_cliente,
    }

def login_view(request):
    # Verifica si el usuario ya está autenticado
    if request.user.is_authenticated:
        # Redirige en función del rol del usuario
        if request.user.is_superuser:
            return redirect('admin:index')
        elif request.user.groups.filter(name='Empleados').exists():
            return redirect('dashboardPedidos')
        elif request.user.groups.filter(name='Clientes').exists():
            return redirect('carrito')

    if request.method == 'POST':
        email = request.POST.get('email')  # Cambiar 'username' a 'email' para autenticación
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            # Redirige después de iniciar sesión
            if user.is_superuser:
                return redirect('admin:index')
            elif user.groups.filter(name='Empleados').exists():
                return redirect('dashboardPedidos')
            elif user.groups.filter(name='Clientes').exists():
                return redirect('carrito')
        else:
            messages.error(request, 'Correo o contraseña incorrectos')
    
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, '¡Sesión finalizada con éxito!')
    return redirect('login')

    #FOMULARIO CONTACTO

def signup_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        documento = request.POST['documento']
        primer_nombre = request.POST['primer_nombre']
        segundo_nombre = request.POST.get('segundo_nombre', '')
        primer_apellido = request.POST['primer_apellido']
        segundo_apellido = request.POST.get('segundo_apellido', '')
        telefono = request.POST.get('telefono', '')
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden')
            return redirect('signup')

        try:
            usuario = CustomUser(
                email=email,
                documento=documento,
                primer_nombre=primer_nombre,
                segundo_nombre=segundo_nombre,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido,
                telefono=telefono
            )
            usuario.set_password(password)
            usuario.full_clean()

            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ingresado ya está registrado. Por favor, elija otro.')
                return redirect('signup')

            usuario.save()

            # Asignar grupo de clientes
            try:
                grupo_clientes = Group.objects.get(name='Clientes')
                usuario.groups.add(grupo_clientes)
            except Group.DoesNotExist:
                messages.error(request, 'El grupo "Clientes" no existe en la base de datos.')
                usuario.delete()
                return redirect('signup')

            # Redirigir directamente al login
            messages.success(request, '¡Usuario creado con éxito! Por favor, inicia sesión.')
            return redirect('login')

        except ValidationError as e:
            for field_errors in e.message_dict.values():
                if isinstance(field_errors, list):
                    for error in field_errors:
                        messages.error(request, error)
                else:
                    messages.error(request, field_errors)

            return redirect('signup')

        except IntegrityError:
            messages.error(request, 'Hubo un error al crear el usuario. Por favor, inténtalo de nuevo.')

    return render(request, 'users/signup.html')

@login_required
def perfil_empleado(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado con éxito.')
            return redirect('perfil_empleado')
        else:
            messages.error(request, 'Por favor corrige los errores a continuación.')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'users/perfilEmpleado.html', {'form': form})

def contacto(request):
    mensaje_enviado = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            email = form.cleaned_data['email']
            mensaje = form.cleaned_data['mensaje']
            
            # Enviar correo
            send_mail(
                f'Mensaje de {nombre} con el correo: {email}',
                mensaje,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            mensaje_enviado = True
    else:
        form = ContactForm()
    
    return render(request, 'users/contacto.html', {'form': form, 'mensaje_enviado': mensaje_enviado})

@login_required
def tabla_clientes(request):
    grupo_clientes = Group.objects.get(name="Clientes")
    clientes = CustomUser.objects.filter(groups=grupo_clientes)
    return render(request, 'users/tablaClientes.html', {'clientes': clientes})

@login_required
def tabla_proveedores(request):
    proveedores = Proveedor.objects.all()  # Obtén todos los registros de proveedores
    return render(request, 'users/tablaProveedores.html', {'proveedores': proveedores})


