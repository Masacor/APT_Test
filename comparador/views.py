from django.shortcuts import render, redirect# login
from django.contrib import messages# login
from django.contrib.auth import authenticate, login as auth_login  # login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password # Para sign up
import re # Para sign up
from datetime import datetime # Para sign up

def index(request):
    return render(request, 'index.html')

def login(request):  # ← Ahora puedes usar "login" como nombre de tu vista
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Validaciones básicas
        errors = []
        
        if not email:
            errors.append('El correo electrónico es obligatorio')
        elif '@' not in email:
            errors.append('Ingresa un correo electrónico válido')
            
        if not password:
            errors.append('La contraseña es obligatoria')
        elif len(password) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres')
        
        # Si hay errores, mostrarlos
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Buscar usuario por email (User model usa username, no email)
            try:
                user = User.objects.get(email=email)
                # Autenticar al usuario
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    auth_login(request, user)  # ← Usa el nombre renombrado aquí
                    messages.success(request, f'¡Bienvenido {user.username}!')
                    return redirect('index')  # Redirigir al inicio
                else:
                    messages.error(request, 'Correo o contraseña incorrectos')
                    
            except User.DoesNotExist:
                messages.error(request, 'Correo o contraseña incorrectos')
    
    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        
        # Validaciones
        errors = []
        
        # Validar nombre
        if not nombre:
            errors.append('El nombre es obligatorio')
        elif len(nombre.strip()) < 2:
            errors.append('El nombre debe tener al menos 2 caracteres')
        
        # Validar email
        if not email:
            errors.append('El correo electrónico es obligatorio')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Ingresa un correo electrónico válido')
        elif User.objects.filter(email=email).exists():
            errors.append('Este correo electrónico ya está registrado')
        
        # Validar contraseñas
        if not password1:
            errors.append('La contraseña es obligatoria')
        elif len(password1) < 6:
            errors.append('La contraseña debe tener al menos 6 caracteres')
        elif password1 != password2:
            errors.append('Las contraseñas no coinciden')
        
        # Validar fecha de nacimiento
        if not fecha_nacimiento:
            errors.append('La fecha de nacimiento es obligatoria')
        else:
            try:
                fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
                hoy = datetime.now()
                edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
                
                if edad < 13:
                    errors.append('Debes tener al menos 13 años para registrarte')
                elif edad > 120:
                    errors.append('Por favor ingresa una fecha de nacimiento válida')
                    
            except ValueError:
                errors.append('Formato de fecha inválido')
        
        # Si no hay errores, proceder con el registro
        if not errors:
            try:
                # Crear usuario (usamos el email como username temporalmente)
                username = email.split('@')[0]  # Parte antes del @ como username
                
                # Si el username ya existe, agregar número
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password(password1),
                    first_name=nombre
                )
                
                messages.success(request, '¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.')
                return redirect('login')
                
            except Exception as e:
                errors.append('Error al crear la cuenta. Por favor intenta nuevamente.')
        
        # Mostrar errores
        for error in errors:
            messages.error(request, error)
    
    return render(request, 'signup.html')