from django.shortcuts import render, redirect # login
from django.contrib import messages# login
from django.contrib.auth import authenticate, login as auth_login  # login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password# Para sign up
import re # Para sign up
from datetime import datetime # Para sign up
from .models import Presentacion, Usuario

# Index
def index(request):
    query = request.GET.get('q')  # El texto que el usuario busca
    if query:
        medicamentos = Presentacion.objects.filter(descripcion__icontains=query)
    else:
        medicamentos = Presentacion.objects.all()
    
    return render(request, 'index.html', {'medicamentos': medicamentos, 'query': query})


# login
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        errors = []

        if not email:
            errors.append('El correo electrónico es obligatorio')
        elif '@' not in email:
            errors.append('Ingresa un correo electrónico válido')

        if not password:
            errors.append('La contraseña es obligatoria')
        elif len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres')

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                usuario = Usuario.objects.get(email=email)
                
                # Verificar contraseña
                if usuario.contraseña and check_password(password, usuario.contraseña):
                    # Guardamos sesión manualmente
                    request.session['usuario_id'] = usuario.idusuario
                    request.session['usuario_nombre'] = usuario.nombre
                    messages.success(request, f'¡Bienvenido {usuario.nombre}!')
                    return redirect('index')
                else:
                    messages.error(request, 'Correo o contraseña incorrectos')

            except Usuario.DoesNotExist:
                messages.error(request, 'Correo o contraseña incorrectos')

    return render(request, 'login.html')


# Sign up
def signup(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        errors = []

        # Validaciones
        if not nombre or len(nombre.strip()) < 2:
            errors.append('El nombre debe tener al menos 2 caracteres.')
        if not email or '@' not in email:
            errors.append('Correo electrónico inválido.')
        elif Usuario.objects.filter(email=email).exists():
            errors.append('Este correo electrónico ya está registrado.')
        if not password1 or len(password1) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres.')
        elif password1 != password2:
            errors.append('Las contraseñas no coinciden.')
        try:
            fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        except Exception:
            errors.append('Fecha de nacimiento inválida.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signup.html')

        # Crear usuario
        try:
            Usuario.objects.create(
                nombre=nombre,
                email=email,
                contraseña=make_password(password1),
                fechanacimiento=fecha_nac
            )
            messages.success(request, '¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')

    return render(request, 'signup.html')