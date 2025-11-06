from django.shortcuts import render, redirect, get_object_or_404 # login y admin
from django.contrib import messages# login
from django.contrib.auth import authenticate, login as auth_login  # login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password# Para sign up
import re # Para sign up
from datetime import datetime # Para sign up
from .models import Presentacion, PrincipioActivo, Usuario, PrecioFarmacia, Medicamento, MedicamentoPrincipio, Laboratorio, MarcaComercial, FormaFarmaceutica, ViasAdministracion
from django.db.models import Min, Max

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


def landing(request):
    total_medicamentos = Presentacion.objects.count()
    total_precios = PrecioFarmacia.objects.count()
    total_usuarios = Usuario.objects.count()

    return render(request, 'landing.html', {
        'total_medicamentos': total_medicamentos,
        'total_precios': total_precios,
        'total_usuarios': total_usuarios,
    })

# --------------- Logout
def logout(request):
    request.session.flush()
    return redirect('index')

# ---------------------------------------------------
"""
def buscador_prueba(request):
    query = request.GET.get('q', '').strip()
    resultados = []

    if query:
        # Filtrar presentaciones que contengan la búsqueda
        presentaciones = Presentacion.objects.filter(descripcion__icontains=query)

        for p in presentaciones:
            # Obtener todos los precios asociados a esta presentación
            precios = PrecioFarmacia.objects.filter(idpresentacion=p)
            if precios.exists():
                resultados.append({
                    'presentacion': p,
                    'farmacias': precios.order_by('precio')  # opcional: ordena por precio ascendente
                })

    context = {
        'query': query,
        'resultados': resultados
    }
    return render(request, 'buscador_prueba.html', context)

"""
def buscador_prueba(request):
    query = request.GET.get('q', '').strip()
    filtros_marcas = request.GET.getlist('marca')
    filtros_principios = request.GET.getlist('principio')
    filtros_vias = request.GET.getlist('via')
    precio_min_input = request.GET.get('precio_min')
    precio_max_input = request.GET.get('precio_max')

    resultados = []

    # Limpiar valores vacíos
    filtros_marcas = [int(f) for f in filtros_marcas if f.isdigit()]
    filtros_principios = [int(f) for f in filtros_principios if f.isdigit()]
    filtros_vias = [int(f) for f in filtros_vias if f.isdigit()]

    # Filtrar presentaciones
    presentaciones = Presentacion.objects.all()
    if query:
        presentaciones = presentaciones.filter(descripcion__icontains=query)

    if filtros_marcas:
        presentaciones = presentaciones.filter(
            idmedicamento__idmarca__idmarca__in=filtros_marcas
        )

    if filtros_principios:
        presentaciones = presentaciones.filter(
            idmedicamento__medicamentoprincipio__idprincipio__in=filtros_principios
        )

    if filtros_vias:
        presentaciones = presentaciones.filter(
            idmedicamento__id_via__id_via__in=filtros_vias
        )

    if precio_min_input:
        presentaciones = presentaciones.filter(preciofarmacia__precio__gte=precio_min_input)
    if precio_max_input:
        presentaciones = presentaciones.filter(preciofarmacia__precio__lte=precio_max_input)

    presentaciones = presentaciones.distinct()

    # Obtener resultados con precio mínimo
    for presentacion in presentaciones:
        precio_obj = PrecioFarmacia.objects.filter(idpresentacion=presentacion).order_by('precio').first()
        if precio_obj:
            resultados.append({
                'presentacion': presentacion,
                'precio': precio_obj.precio,  # solo el valor numérico
                'farmacia': precio_obj.idfarmacia.nombrefarmacia,  # nombre de la farmacia
            })

    # IDs de medicamentos en resultados
    medicamentos_ids = presentaciones.values_list('idmedicamento_id', flat=True).distinct()

    # Filtros dinámicos basados en resultados
    marcas_disponibles = MarcaComercial.objects.filter(
        idmarca__in=medicamentos_ids
    ).distinct()

    principios_disponibles = PrincipioActivo.objects.filter(
        medicamentoprincipio__idmedicamento_id__in=medicamentos_ids
    ).distinct()

    vias_disponibles = ViasAdministracion.objects.filter(
        id_via__in=medicamentos_ids
    ).distinct()

    # Precio global de la búsqueda (para slider)
    precio_global = PrecioFarmacia.objects.aggregate(
        precio_min=Min('precio'),
        precio_max=Max('precio')
    )
    precio_min = precio_global['precio_min'] or 0
    precio_max = precio_global['precio_max'] or 1000

    context = {
        'query': query,
        'resultados': resultados,
        'marcas': marcas_disponibles,
        'principios': principios_disponibles,
        'vias': vias_disponibles,
        'filtros_marcas': [str(f) for f in filtros_marcas],
        'filtros_principios': [str(f) for f in filtros_principios],
        'filtros_vias': [str(f) for f in filtros_vias],
        'precio_min': precio_min,
        'precio_max': precio_max,
        'filtro_min': precio_min_input or precio_min,
        'filtro_max': precio_max_input or precio_max,
    }

    return render(request, 'buscador_prueba.html', context)



def informacion_presentacion(request, descripcion):
    presentacion = get_object_or_404(Presentacion, descripcion=descripcion)
    precios = PrecioFarmacia.objects.filter(idpresentacion=presentacion).order_by('precio')
    
    context = {
        'presentacion': presentacion,
        'precios': precios
    }
    return render(request, 'informacion_presentacion.html', context)













# --------------------- CRUDS de todo
def admin_medicamentos(request):
    # --- Crear nuevo medicamento ---
    if request.method == 'POST' and 'crear_medicamento' in request.POST:
        registrosanitario = request.POST.get('registrosanitario', '').strip()
        idlaboratorio = request.POST.get('idlaboratorio') or None
        idmarca = request.POST.get('idmarca') or None
        idforma = request.POST.get('idforma') or None
        id_via = request.POST.get('id_via') or None
        url_foto = request.POST.get('url_foto', '').strip()

        try:
            medicamento = Medicamento(
                registrosanitario=registrosanitario,
                idlaboratorio=Laboratorio.objects.get(pk=idlaboratorio) if idlaboratorio else None,
                idmarca=MarcaComercial.objects.get(pk=idmarca) if idmarca else None,
                idforma=FormaFarmaceutica.objects.get(pk=idforma) if idforma else None,
                id_via=ViasAdministracion.objects.get(pk=id_via) if id_via else None,
                url_foto=url_foto
            )
            medicamento.save()
            messages.success(request, 'Medicamento creado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al crear el medicamento: {str(e)}')
        return redirect('admin_medicamentos')

    # --- Editar medicamento ---
    if request.method == 'POST' and 'editar_medicamento' in request.POST:
        medicamento_id = request.POST.get('idmedicamento')
        medicamento = get_object_or_404(Medicamento, pk=medicamento_id)

        medicamento.registrosanitario = request.POST.get('registrosanitario', '').strip()
        idlaboratorio = request.POST.get('idlaboratorio') or None
        idmarca = request.POST.get('idmarca') or None
        idforma = request.POST.get('idforma') or None
        id_via = request.POST.get('id_via') or None
        medicamento.url_foto = request.POST.get('url_foto', '').strip()

        try:
            medicamento.idlaboratorio = Laboratorio.objects.get(pk=idlaboratorio) if idlaboratorio else None
            medicamento.idmarca = MarcaComercial.objects.get(pk=idmarca) if idmarca else None
            medicamento.idforma = FormaFarmaceutica.objects.get(pk=idforma) if idforma else None
            medicamento.id_via = ViasAdministracion.objects.get(pk=id_via) if id_via else None
            medicamento.save()
            messages.success(request, 'Medicamento actualizado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al actualizar el medicamento: {str(e)}')
        return redirect('admin_medicamentos')

    # --- Eliminar medicamento ---
    if request.method == 'POST' and 'eliminar_medicamento' in request.POST:
        medicamento_id = request.POST.get('idmedicamento')
        medicamento = get_object_or_404(Medicamento, pk=medicamento_id)
        try:
            medicamento.delete()
            messages.success(request, 'Medicamento eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el medicamento: {str(e)}')
        return redirect('admin_medicamentos')

    # --- Datos para mostrar en la tabla y selects ---
    medicamentos = Medicamento.objects.all()
    laboratorios = Laboratorio.objects.all()
    marcas = MarcaComercial.objects.all()
    formas = FormaFarmaceutica.objects.all()
    vias = ViasAdministracion.objects.all()

    context = {
        'medicamentos': medicamentos,
        'laboratorios': laboratorios,
        'marcas': marcas,
        'formas': formas,
        'vias': vias,
    }
    return render(request, 'admin_medicamentos.html', context)
# ---------------------------------------------------

# ------------------ Presentacion
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Presentacion, Medicamento

def presentacion(request):
    if request.method == "POST":
        action = request.POST.get("action")
        id_presentacion = request.POST.get("idpresentacion")
        idmedicamento = request.POST.get("idmedicamento") or None
        cantidadvalor = request.POST.get("cantidadvalor")
        cantidadunidad = request.POST.get("cantidadunidad")
        descripcion = request.POST.get("descripcion")

        # Convertir idmedicamento a objeto Medicamento o None
        medicamento = Medicamento.objects.filter(idmedicamento=idmedicamento).first() if idmedicamento else None

        if action == "crear":
            Presentacion.objects.create(
                idmedicamento=medicamento,
                cantidadvalor=cantidadvalor,
                cantidadunidad=cantidadunidad,
                descripcion=descripcion
            )
            messages.success(request, "Presentación creada correctamente.")
        elif action == "editar" and id_presentacion:
            present = get_object_or_404(Presentacion, idpresentacion=id_presentacion)
            present.idmedicamento = medicamento
            present.cantidadvalor = cantidadvalor
            present.cantidadunidad = cantidadunidad
            present.descripcion = descripcion
            present.save()
            messages.success(request, "Presentación actualizada correctamente.")
        elif action == "eliminar" and id_presentacion:
            present = get_object_or_404(Presentacion, idpresentacion=id_presentacion)
            present.delete()
            messages.success(request, "Presentación eliminada correctamente.")
        else:
            messages.error(request, "Error en la acción realizada.")

        return redirect("presentacion")

    # GET
    presentaciones = Presentacion.objects.all().select_related('idmedicamento')
    medicamentos = Medicamento.objects.all()
    return render(request, "admin_presentacion.html", {
        "presentaciones": presentaciones,
        "medicamentos": medicamentos
    })
