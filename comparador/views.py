from django.shortcuts import render, redirect, get_object_or_404 # login y admin
from django.contrib import messages# login
from django.contrib.auth import authenticate, login as auth_login  # login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password# Para sign up
import re # Para sign up
from datetime import datetime # Para sign up
from .models import Presentacion, Usuario, PrecioFarmacia, Medicamento
from django.db.models import Min

# # Index
# def index(request):
#     query = request.GET.get('q')  # El texto que el usuario busca
#     if query:
#         medicamentos = Presentacion.objects.filter(descripcion__icontains=query)
#     else:
#         medicamentos = Presentacion.objects.all()
    
#     return render(request, 'index.html', {'medicamentos': medicamentos, 'query': query})

# def index(request):
#     query = request.GET.get('q')
    
#     if query:
#         presentaciones = Presentacion.objects.filter(descripcion__icontains=query)
#     else:
#         presentaciones = Presentacion.objects.all()
    
#     resultados = []
    
#     for p in presentaciones:
#         # Todos los precios asociados a esa presentación
#         precios = PrecioFarmacia.objects.filter(idpresentacion=p)
        
#         # Si hay precios
#         for precio in precios:
#             resultados.append({
#                 'farmacia': precio.idfarmacia.nombrefarmacia,
#                 'farmacia_url': precio.idfarmacia.url,
#                 'precio': precio.precio,
#                 'precio_oferta': precio.preciooferta,
#                 'presentacion': p.descripcion,
#                 'medicamento': p.idmedicamento.registrosanitario if p.idmedicamento else "",
#                 'marca': p.idmedicamento.idmarca.nombremarca if p.idmedicamento and p.idmedicamento.idmarca else "",
#                 'laboratorio': p.idmedicamento.idlaboratorio.nombrelaboratorio if p.idmedicamento and p.idmedicamento.idlaboratorio else "",
#             })

#     return render(request, 'index.html', {'resultados': resultados, 'query': query})

def index(request):
    query = request.GET.get('q', '')
    resultados = []

    presentaciones = Presentacion.objects.filter(descripcion__icontains=query) if query else Presentacion.objects.all()

    for p in presentaciones:
        precios = PrecioFarmacia.objects.filter(idpresentacion=p)
        precios_por_farmacia = precios.values('idfarmacia').annotate(min_precio=Min('precio'))

        for item in precios_por_farmacia:
            precio_obj = precios.filter(idfarmacia=item['idfarmacia'], precio=item['min_precio']).first()
            medicamento = p.idmedicamento  # ForeignKey

            resultados.append({
                'farmacia': precio_obj.idfarmacia.nombrefarmacia,
                'precio': precio_obj.precio,
                'precio_oferta': precio_obj.preciooferta,
                'presentacion': f"{p.descripcion} ({p.cantidadvalor} {p.cantidadunidad})",
                'marca': medicamento.idmarca.nombremarca if medicamento.idmarca else '',
                'laboratorio': medicamento.idlaboratorio.nombrelaboratorio if medicamento.idlaboratorio else '',
                'farmacia_url': precio_obj.presentacionurl
            })

    return render(request, 'index.html', {'resultados': resultados, 'query': query})



# login
# def login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         errors = []

#         if not email:
#             errors.append('El correo electrónico es obligatorio')
#         elif '@' not in email:
#             errors.append('Ingresa un correo electrónico válido')

#         if not password:
#             errors.append('La contraseña es obligatoria')
#         elif len(password) < 6:
#             errors.append('La contraseña debe tener al menos 6 caracteres')

#         if errors:
#             for error in errors:
#                 messages.error(request, error)
#         else:
#             try:
#                 usuario = Usuario.objects.get(email=email)
                
#                 # Verificar contraseña
#                 if usuario.contraseña and check_password(password, usuario.contraseña):
#                     # Guardamos sesión manualmente
#                     request.session['usuario_id'] = usuario.idusuario
#                     request.session['usuario_nombre'] = usuario.nombre
#                     # messages.success(request, f'¡Bienvenido {usuario.nombre}!')
#                     return redirect('index')
#                 else:
#                     messages.error(request, 'Correo o contraseña incorrectos')

#             except Usuario.DoesNotExist:
#                 messages.error(request, 'Correo o contraseña incorrectos')

#     return render(request, 'login.html')


# --------------------- Login
def login_usuario(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        errors = []

        if not email or '@' not in email:
            errors.append('Correo inválido.')
        if not password:
            errors.append('Contraseña obligatoria.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'login.html')

        try:
            usuario = Usuario.objects.get(email=email)
            if usuario.contraseña and check_password(password, usuario.contraseña):
                # Guardamos sesión
                request.session['usuario_id'] = usuario.idusuario
                request.session['usuario_nombre'] = usuario.nombre
                request.session['is_admin'] = usuario.is_admin

                if usuario.is_admin:
                    return redirect('admin_dashboard')
                else:
                    return redirect('index')
            else:
                messages.error(request, 'Correo o contraseña incorrectos.')
        except Usuario.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'login.html')

# ----------------------  Panel de Admin CRUD
def admin_dashboard(request):
    if not request.session.get('is_admin'):
        return redirect('login')

    # Crear usuario
    # if request.method == 'POST' and 'crear' in request.POST:
    #     nombre = request.POST['nombre']
    #     correo = request.POST['correo']
    #     contraseña = make_password(request.POST['contraseña'])
    #     Usuario.objects.create(nombre=nombre, email=correo, contraseña=contraseña)
    #     return redirect('admin_dashboard')

    if request.method == 'POST' and 'crear' in request.POST:
        nombre = request.POST['nombre']
        correo = request.POST['correo']
        contraseña = make_password(request.POST['contraseña'])  # 🔹 hash
        Usuario.objects.create(nombre=nombre, email=correo, contraseña=contraseña)
        return redirect('admin_dashboard')

    # Editar usuario
    # if request.method == 'POST' and 'editar' in request.POST:
    #     usuario_id = request.POST['usuario_id']
    #     usuario = get_object_or_404(Usuario, idusuario=usuario_id)
    #     usuario.nombre = request.POST['nombre']
    #     usuario.email = request.POST['correo']
    #     if request.POST['contraseña']:
    #         usuario.contraseña = make_password(request.POST['contraseña'])
    #     usuario.save()
    #     return redirect('admin_dashboard')

    if request.method == 'POST' and 'editar' in request.POST:
        usuario_id = request.POST['usuario_id']
        usuario = get_object_or_404(Usuario, idusuario=usuario_id)
        usuario.nombre = request.POST['nombre']
        usuario.email = request.POST['correo']
        if request.POST['contraseña']:
            usuario.contraseña = make_password(request.POST['contraseña'])  # 🔹 hash
        usuario.save()
        return redirect('admin_dashboard')

    # Eliminar usuario
    if request.method == 'POST' and 'eliminar' in request.POST:
        usuario_id = request.POST['usuario_id']
        usuario = get_object_or_404(Usuario, idusuario=usuario_id)
        usuario.delete()
        return redirect('admin_dashboard')


    # Listar usuarios
    usuarios = Usuario.objects.all()
    return render(request, 'admin_dashboard.html', {'usuarios': usuarios})



# ----------------------- Sign up
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


# --------------- Logout
def logout(request):
    request.session.flush()
    return redirect('index')
