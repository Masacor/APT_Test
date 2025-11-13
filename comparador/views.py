from django.shortcuts import render, redirect, get_object_or_404 # login y admin
from django.contrib import messages# login
from django.contrib.auth import authenticate, login as auth_login  # login
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password# Para sign up
import re # Para sign up
from datetime import datetime, date # Para sign up
from .models import Presentacion, PrincipioActivo, Usuario, PrecioFarmacia, Medicamento, MedicamentoPrincipio, Laboratorio, MarcaComercial, FormaFarmaceutica, ViasAdministracion, Guardado
from django.db.models import Min, Max
from django.http import Http404, JsonResponse
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError




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
# def admin_dashboard(request):
#     if not request.session.get('is_admin'):
#         return redirect('login')

#     # Crear usuario
#     # if request.method == 'POST' and 'crear' in request.POST:
#     #     nombre = request.POST['nombre']
#     #     correo = request.POST['correo']
#     #     contraseña = make_password(request.POST['contraseña'])
#     #     Usuario.objects.create(nombre=nombre, email=correo, contraseña=contraseña)
#     #     return redirect('admin_dashboard')

#     if request.method == 'POST' and 'crear' in request.POST:
#         nombre = request.POST['nombre']
#         correo = request.POST['correo']
#         contraseña = make_password(request.POST['contraseña'])  # 🔹 hash
#         Usuario.objects.create(nombre=nombre, email=correo, contraseña=contraseña)
#         return redirect('admin_dashboard')

#     # Editar usuario
#     # if request.method == 'POST' and 'editar' in request.POST:
#     #     usuario_id = request.POST['usuario_id']
#     #     usuario = get_object_or_404(Usuario, idusuario=usuario_id)
#     #     usuario.nombre = request.POST['nombre']
#     #     usuario.email = request.POST['correo']
#     #     if request.POST['contraseña']:
#     #         usuario.contraseña = make_password(request.POST['contraseña'])
#     #     usuario.save()
#     #     return redirect('admin_dashboard')

#     if request.method == 'POST' and 'editar' in request.POST:
#         usuario_id = request.POST['usuario_id']
#         usuario = get_object_or_404(Usuario, idusuario=usuario_id)
#         usuario.nombre = request.POST['nombre']
#         usuario.email = request.POST['correo']
#         if request.POST['contraseña']:
#             usuario.contraseña = make_password(request.POST['contraseña'])  # 🔹 hash
#         usuario.save()
#         return redirect('admin_dashboard')

#     # Eliminar usuario
#     if request.method == 'POST' and 'eliminar' in request.POST:
#         usuario_id = request.POST['usuario_id']
#         usuario = get_object_or_404(Usuario, idusuario=usuario_id)
#         usuario.delete()
#         return redirect('admin_dashboard')


#     # Listar usuarios
#     usuarios = Usuario.objects.all()
#     return render(request, 'admin_dashboard.html', {'usuarios': usuarios})



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


def buscador_prueba(request):
    query = request.GET.get('q', '').strip()
    filtros_marcas = request.GET.getlist('marca')
    filtros_principios = request.GET.getlist('principio')
    filtros_vias = request.GET.getlist('via')
    precio_filtro = request.GET.get('precio')  # Ahora solo un precio

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

    if precio_filtro:
        # Si hay un precio seleccionado, filtramos presentaciones menores o iguales a ese precio
        presentaciones = presentaciones.filter(preciofarmacia__precio__lte=precio_filtro)

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
        'precio_actual': precio_filtro or precio_max,  # Valor actual del slider (por defecto el máximo)
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


'''
def detalle_presentacion(request, id):
    """Mostrar detalle de una presentación por su id (idpresentacion).

    Antes la vista intentaba buscar por `slug` pero el modelo de
    `Presentacion` no define un campo `slug`. Aquí usamos el PK
    `idpresentacion` para garantizar que la vista funcione con los
    registros existentes.
    """
    presentacion = get_object_or_404(Presentacion, pk=id)

    # Precios asociados (agrupados por URL y tomando el más reciente por ID y fecha)
    from django.db.models import Max
    
    # Primero obtenemos los URLs únicos y su ID más reciente
    urls_recientes = PrecioFarmacia.objects.filter(
        idpresentacion=presentacion
    ).values('presentacionurl').annotate(
        ultimo_id=Max('idprecio'),
        ultima_fecha=Max('fecharegistro')
    )
    
    # Luego obtenemos los precios más recientes para cada URL
    precios = []
    for url_data in urls_recientes:
        precio_reciente = PrecioFarmacia.objects.filter(
            idpresentacion=presentacion,
            presentacionurl=url_data['presentacionurl'],
            idprecio=url_data['ultimo_id'],
            fecharegistro=url_data['ultima_fecha']
        ).first()
        if precio_reciente:
            precios.append(precio_reciente)
    
    # Ordenamos la lista final por precio
    precios.sort(key=lambda x: x.precio)

    # Datos del medicamento relacionado (si existe)
    medicamento = presentacion.idmedicamento
    marca = None
    laboratorio = None
    principios = PrincipioActivo.objects.none()
    if medicamento:
        marca = medicamento.idmarca if hasattr(medicamento, 'idmarca') else None
        laboratorio = medicamento.idlaboratorio if hasattr(medicamento, 'idlaboratorio') else None
        # Principios activos asociados al medicamento
        principios = PrincipioActivo.objects.filter(medicamentoprincipio__idmedicamento=medicamento).distinct()

    context = {
        'presentacion': presentacion,
        'medicamento': medicamento,
        'marca': marca,
        'laboratorio': laboratorio,
        'principios': principios,
        'precios': precios,
    }

    return render(request, 'detalle_presentacion.html', context)
'''
def detalle_presentacion(request, id):
    """Mostrar detalle de una presentación por su id (idpresentacion).

    Antes la vista intentaba buscar por `slug` pero el modelo de
    `Presentacion` no define un campo `slug`. Aquí usamos el PK
    `idpresentacion` para garantizar que la vista funcione con los
    registros existentes.
    """
    presentacion = get_object_or_404(Presentacion, pk=id)

    # Datos del medicamento relacionado (si existe)
    medicamento = presentacion.idmedicamento
    marca = None
    laboratorio = None
    principios = PrincipioActivo.objects.none()
    
    # Intentar obtener marca y laboratorio del medicamento
    if medicamento:
        marca = medicamento.idmarca
        laboratorio = medicamento.idlaboratorio
        # Principios activos asociados al medicamento
        principios = PrincipioActivo.objects.filter(medicamentoprincipio__idmedicamento=medicamento).distinct()
    
    # Si no hay marca/laboratorio en medicamento, obtenerlos de la tabla presentacion directamente
    if not marca or not laboratorio:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT idmarca, idlaboratorio FROM presentacion WHERE idpresentacion = %s",
                [id]
            )
            row = cursor.fetchone()
            if row and row[0]:  # Si hay idmarca
                marca = MarcaComercial.objects.filter(pk=row[0]).first()
            if row and row[1]:  # Si hay idlaboratorio
                laboratorio = Laboratorio.objects.filter(pk=row[1]).first()

    # Precios asociados - obtener TODOS los precios, no agrupados
    precios = PrecioFarmacia.objects.filter(
        idpresentacion=presentacion
    ).select_related('idfarmacia').order_by('precio')

    context = {
        'presentacion': presentacion,
        'medicamento': medicamento,
        'marca': marca,
        'laboratorio': laboratorio,
        'principios': principios,
        'precios': precios,
    }

    # Indicador de usuario logueado (se establece en login_usuario)
    context['user_logged'] = bool(request.session.get('usuario_id'))
    
    # Verificar si el usuario ya tiene guardada esta presentación
    if context['user_logged']:
        usuario_id = request.session.get('usuario_id')
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
            context['is_saved'] = Guardado.objects.filter(
                idusuario=usuario,
                idpresentacion=presentacion
            ).exists()
        except Usuario.DoesNotExist:
            context['is_saved'] = False
    else:
        context['is_saved'] = False

    return render(request, 'detalle_presentacion.html', context)






#------------------------------ BOTON DE GUARDAR MEDICAMENTOS
def guardar_presentacion(request):
    """Endpoint POST para guardar o eliminar una presentación (crear/borrar Guardado)."""
    if request.method == 'POST':
        usuario_id = request.session.get('usuario_id')
        presentacion_id = request.POST.get('presentacion_id')
        
        # Validar que el usuario esté logueado
        if not usuario_id:
            return JsonResponse({'success': False, 'message': 'Usuario no logueado'}, status=401)
        
        # Validar que la presentación exista
        try:
            presentacion = Presentacion.objects.get(pk=presentacion_id)
        except Presentacion.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Presentación no encontrada'}, status=404)
        
        # Obtener el usuario
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Usuario no encontrado'}, status=404)
        
        # Verificar si ya existe un guardado
        guardado_existente = Guardado.objects.filter(
            idusuario=usuario,
            idpresentacion=presentacion
        ).first()
        
        if guardado_existente:
            # Si existe, lo eliminamos (desmarcar)
            guardado_existente.delete()
            return JsonResponse({
                'success': True, 
                'message': 'Presentación removida de guardados',
                'action': 'removed'
            })
        else:
            # Si no existe, lo creamos (marcar)
            try:
                guardado = Guardado.objects.create(
                    idusuario=usuario,
                    idpresentacion=presentacion,
                    fechaagregado=date.today()
                )
                return JsonResponse({
                    'success': True, 
                    'message': 'Presentación guardada correctamente',
                    'action': 'saved',
                    'guardado_id': guardado.idguardado
                })
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'Error al guardar: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

























































# --------------------- CRUDS de todo

# ----------------------- DASHBOARD
def admin_dashboard(request):
    if not request.session.get('is_admin'):
        return redirect('login')
    
    return render(request, 'admin_dashboard.html')
# -----------------------

# -------------------- Usuario
def admin_usuario(request):
    if not request.session.get('is_admin'):
        return redirect('login')

    # Crear usuario
    if request.method == 'POST' and 'crear' in request.POST:
        nombre = request.POST['nombre']
        correo = request.POST['correo']
        contraseña = make_password(request.POST['contraseña'])  # 🔹 hash
        Usuario.objects.create(nombre=nombre, email=correo, contraseña=contraseña)
        return redirect('admin_usuario')  # 🔹 redirige a la nueva view

    # Editar usuario
    if request.method == 'POST' and 'editar' in request.POST:
        usuario_id = request.POST['usuario_id']
        usuario = get_object_or_404(Usuario, idusuario=usuario_id)
        usuario.nombre = request.POST['nombre']
        usuario.email = request.POST['correo']
        if request.POST['contraseña']:
            usuario.contraseña = make_password(request.POST['contraseña'])  # 🔹 hash
        usuario.save()
        return redirect('admin_usuario')

    # Eliminar usuario
    if request.method == 'POST' and 'eliminar' in request.POST:
        usuario_id = request.POST['usuario_id']
        usuario = get_object_or_404(Usuario, idusuario=usuario_id)
        usuario.delete()
        return redirect('admin_usuario')


    # Listar usuarios
    usuarios = Usuario.objects.all()
    return render(request, 'admin_usuario.html', {'usuarios': usuarios})  # 🔹 nuevo html

# --------------------------------

# ------------------------------- Medicamentos
def admin_medicamentos(request):
    if not request.session.get('is_admin'):
        return redirect('login')

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
    if not request.session.get('is_admin'):
        return redirect('login')


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
# ---------------------

# --------------------- Laboratorio
def laboratorio(request):
    if not request.session.get('is_admin'):
        return redirect('login')

    # Crear nuevo laboratorio
    if request.method == 'POST':
        if 'agregar' in request.POST:
            nombre = request.POST.get('nombrelaboratorio', '').strip()

            # Validaciones
            if not nombre:
                messages.error(request, "El nombre del laboratorio no puede estar vacío.")
            elif Laboratorio.objects.filter(nombrelaboratorio__iexact=nombre).exists():
                messages.error(request, "Ya existe un laboratorio con ese nombre.")
            else:
                Laboratorio.objects.create(nombrelaboratorio=nombre)
                messages.success(request, "Laboratorio agregado correctamente.")
            return redirect('laboratorio')

        # Editar laboratorio existente
        elif 'editar' in request.POST:
            idlaboratorio = request.POST.get('idlaboratorio')
            nombre = request.POST.get('nombrelaboratorio', '').strip()

            try:
                lab = Laboratorio.objects.get(pk=idlaboratorio)
                if not nombre:
                    messages.error(request, "El nombre del laboratorio no puede estar vacío.")
                elif Laboratorio.objects.filter(nombrelaboratorio__iexact=nombre).exclude(pk=idlaboratorio).exists():
                    messages.error(request, "Ya existe un laboratorio con ese nombre.")
                else:
                    lab.nombrelaboratorio = nombre
                    lab.save()
                    messages.success(request, "Laboratorio actualizado correctamente.")
            except Laboratorio.DoesNotExist:
                messages.error(request, "El laboratorio no existe.")

            return redirect('laboratorio')

        # Eliminar laboratorio
        elif 'eliminar' in request.POST:
            idlaboratorio = request.POST.get('idlaboratorio')
            try:
                lab = Laboratorio.objects.get(pk=idlaboratorio)
                lab.delete()
                messages.success(request, "Laboratorio eliminado correctamente.")
            except Laboratorio.DoesNotExist:
                messages.error(request, "El laboratorio no existe.")
            return redirect('laboratorio')

    # Listar todos los laboratorios
    laboratorios = Laboratorio.objects.all().order_by('idlaboratorio')
    return render(request, 'admin_laboratorio.html', {'laboratorios': laboratorios})
# ---------------------------------------------------------

# --------------------------- Marcacomercial
def marcacomercial(request):
    if not request.session.get('is_admin'):
        return redirect('login')

    """
    Vista basada en funciones para CRUD de MarcaComercial.
    Soporta acciones por botones: agregar, editar y eliminar (según name del submit).
    """
    if request.method == 'POST':
        # --- AGREGAR ---
        if 'agregar' in request.POST:
            nombremarca = (request.POST.get('nombremarca') or '').strip()
            if not nombremarca:
                messages.error(request, "El nombre de la marca no puede estar vacío.")
                return redirect('admin_marcacomercial')
            try:
                # Crear nuevo registro
                MarcaComercial.objects.create(nombremarca=nombremarca)
                messages.success(request, "Marca creada correctamente.")
            except Exception as e:
                # captura general de error de BD
                messages.error(request, f"Ocurrió un error al crear: {str(e)}")
            return redirect('admin_marcacomercial')

        # --- EDITAR ---
        if 'editar' in request.POST:
            idmarca = request.POST.get('idmarca')
            nombremarca = (request.POST.get('nombremarca') or '').strip()
            if not nombremarca:
                messages.error(request, "El nombre de la marca no puede estar vacío.")
                return redirect('admin_marcacomercial')
            try:
                marca = get_object_or_404(MarcaComercial, pk=idmarca)
                marca.nombremarca = nombremarca
                marca.save()
                messages.success(request, "Marca actualizada correctamente.")
            except Exception as e:
                messages.error(request, f"Ocurrió un error al actualizar: {str(e)}")
            return redirect('admin_marcacomercial')

        # --- ELIMINAR ---
        if 'eliminar' in request.POST:
            idmarca = request.POST.get('idmarca')
            try:
                marca = get_object_or_404(MarcaComercial, pk=idmarca)
                # intentar eliminar en bloque try/except para controlar errores por FK
                with transaction.atomic():
                    marca.delete()
                messages.success(request, "Marca eliminada correctamente.")
            except ProtectedError:
                messages.error(request, "No se puede eliminar la marca porque está referenciada en otro registro.")
            except IntegrityError:
                messages.error(request, "No se puede eliminar la marca por restricciones en la base de datos.")
            except Exception as e:
                messages.error(request, f"Ocurrió un error al eliminar: {str(e)}")
            return redirect('admin_marcacomercial')

    # GET -> mostrar lista
    marcas = MarcaComercial.objects.all().order_by('idmarca')
    context = {
        'marcas': marcas,
    }
    return render(request, 'admin_marcacomercial.html', context)
# ----------------------------------------

# --------------- Vias_administracion
def vias_administracion(request):
    if not request.session.get('is_admin'):
        return redirect('login')

    """
    Vista FBV para administrar la tabla vias_administracion.
    Maneja acciones: agregar, editar, eliminar a través del nombre del botón en el POST.
    """
    if request.method == 'POST':
        # --- AGREGAR nueva vía ---
        if 'agregar' in request.POST:
            via = request.POST.get('via', '').strip()
            descripcion = request.POST.get('descripcion', '').strip()

            # Validaciones requeridas
            if not via:
                messages.error(request, "El nombre de la vía no puede estar vacío.")
            elif not descripcion:
                messages.error(request, "La descripción no puede estar vacía.")
            else:
                try:
                    nueva = ViasAdministracion(via=via, descripcion=descripcion)
                    nueva.save()
                    messages.success(request, "Vía de administración creada correctamente.")
                    return redirect('admin_vias_administracion')
                except Exception as e:
                    # Mensaje genérico si falla creación por otra razón
                    messages.error(request, f"No se pudo crear la vía: {str(e)}")

        # --- EDITAR vía existente ---
        elif 'editar' in request.POST:
            try:
                id_via = request.POST.get('id_via')
                via_val = request.POST.get('via', '').strip()
                descripcion_val = request.POST.get('descripcion', '').strip()

                # Validaciones
                if not via_val:
                    messages.error(request, "El nombre de la vía no puede estar vacío.")
                elif not descripcion_val:
                    messages.error(request, "La descripción no puede estar vacía.")
                else:
                    try:
                        via_obj = ViasAdministracion.objects.get(pk=id_via)
                        via_obj.via = via_val
                        via_obj.descripcion = descripcion_val
                        via_obj.save()
                        messages.success(request, "Vía actualizada correctamente.")
                        return redirect('admin_vias_administracion')
                    except ViasAdministracion.DoesNotExist:
                        messages.error(request, "La vía a editar no existe.")
            except Exception as e:
                messages.error(request, f"No se pudo editar la vía: {str(e)}")

        # --- ELIMINAR vía ---
        elif 'eliminar' in request.POST:
            id_via = request.POST.get('id_via')
            try:
                via_obj = ViasAdministracion.objects.get(pk=id_via)
                try:
                    via_obj.delete()
                    messages.success(request, "Vía eliminada correctamente.")
                    return redirect('admin_vias_administracion')
                except IntegrityError:
                    # Si existe restricción FK con medicamentos u otra tabla
                    messages.error(request, "No se puede eliminar la vía porque está asociada a uno o más medicamentos.")
                except Exception as e:
                    messages.error(request, f"No se pudo eliminar la vía: {str(e)}")
            except ViasAdministracion.DoesNotExist:
                messages.error(request, "La vía a eliminar no existe.")

    # GET y render de listado
    vias = ViasAdministracion.objects.all().order_by('id_via')
    context = {
        'vias': vias,
    }
    return render(request, 'admin_vias_administracion.html', context)
# -------------------------------------------------

# ----------------------- FormaFarmaceutica
def formafarmaceutica(request):
    if not request.session.get('is_admin'):
        return redirect('login')

    # Crear nueva forma farmacéutica
    if request.method == 'POST' and 'agregar' in request.POST:
        nombre = request.POST.get('nombreforma', '').strip()
        if not nombre:
            messages.error(request, "El nombre de la forma farmacéutica no puede estar vacío.")
        else:
            try:
                FormaFarmaceutica.objects.create(nombreforma=nombre)
                messages.success(request, f"Forma farmacéutica '{nombre}' creada correctamente.")
            except Exception as e:
                messages.error(request, f"No se pudo crear la forma farmacéutica: {str(e)}")

        return redirect('admin_formafarmaceutica')

    # Editar forma farmacéutica existente
    if request.method == 'POST' and 'editar' in request.POST:
        idforma = request.POST.get('idforma')
        nombre = request.POST.get('nombreforma', '').strip()
        if not nombre:
            messages.error(request, "El nombre de la forma farmacéutica no puede estar vacío.")
        else:
            try:
                forma = FormaFarmaceutica.objects.get(idforma=idforma)
                forma.nombreforma = nombre
                forma.save()
                messages.success(request, f"Forma farmacéutica actualizada correctamente.")
            except FormaFarmaceutica.DoesNotExist:
                messages.error(request, "La forma farmacéutica no existe.")
            except Exception as e:
                messages.error(request, f"No se pudo actualizar la forma farmacéutica: {str(e)}")
        return redirect('admin_formafarmaceutica')

    # Eliminar forma farmacéutica
    if request.method == 'POST' and 'eliminar' in request.POST:
        idforma = request.POST.get('idforma')
        try:
            forma = FormaFarmaceutica.objects.get(idforma=idforma)
            forma.delete()
            messages.success(request, f"Forma farmacéutica eliminada correctamente.")
        except FormaFarmaceutica.DoesNotExist:
            messages.error(request, "La forma farmacéutica no existe.")
        except IntegrityError:
            messages.error(request, "No se puede eliminar esta forma farmacéutica porque está referenciada en otros registros.")
        except Exception as e:
            messages.error(request, f"No se pudo eliminar la forma farmacéutica: {str(e)}")
        return redirect('admin_formafarmaceutica')

    # Mostrar todas las formas farmacéuticas
    formas = FormaFarmaceutica.objects.all().order_by('idforma')
    return render(request, 'admin_formafarmaceutica.html', {'formas': formas})
# -----------------------------------

# -------------------- PrincipioActivo
def principioactivo(request):
    if not request.session.get('is_admin'):
        return redirect('login')

    if request.method == 'POST':
        # AGREGAR
        if 'agregar' in request.POST:
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.error(request, "El nombre del principio activo no puede estar vacío.")
            else:
                try:
                    PrincipioActivo.objects.create(nombre=nombre)
                    messages.success(request, "Principio activo agregado correctamente.")
                    return redirect('admin_principioactivo')
                except Exception as e:
                    messages.error(request, f"Error al agregar el principio activo: {e}")

        # EDITAR
        elif 'editar' in request.POST:
            idprincipio = request.POST.get('idprincipio')
            nombre = request.POST.get('nombre', '').strip()
            if not nombre:
                messages.error(request, "El nombre del principio activo no puede estar vacío.")
            else:
                try:
                    principio = get_object_or_404(PrincipioActivo, pk=idprincipio)
                    principio.nombre = nombre
                    principio.save()
                    messages.success(request, "Principio activo actualizado correctamente.")
                    return redirect('admin_principioactivo')
                except Exception as e:
                    messages.error(request, f"Error al actualizar el principio activo: {e}")

        # ELIMINAR
        elif 'eliminar' in request.POST:
            idprincipio = request.POST.get('idprincipio')
            try:
                principio = get_object_or_404(PrincipioActivo, pk=idprincipio)
                principio.delete()
                messages.success(request, "Principio activo eliminado correctamente.")
                return redirect('admin_principioactivo')
            except Exception as e:
                messages.error(request, f"No se puede eliminar este principio activo: {e}")

    # LEER
    principios = PrincipioActivo.objects.all().order_by('idprincipio')
    return render(request, 'admin_principioactivo.html', {'principios': principios})
# --------------------------------

# ----------------------- PrecioFarmacia
# ----------------------------------------------------------------------------------------------------------


# ----------------------- PERFIL DE USUARIO -----------------------
def perfil_usuario(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, idusuario=usuario_id)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        fechanacimiento = request.POST.get('fechanacimiento', '').strip()

        # Campos de cambio de contraseña
        actual = request.POST.get('actual', '').strip()
        nueva = request.POST.get('nueva', '').strip()
        confirmar = request.POST.get('confirmar', '').strip()

        # Validación básica de nombre/email
        if not nombre or not email:
            messages.error(request, "El nombre y el email son obligatorios.")
            return render(request, 'usuario_perfil.html', {'usuario': usuario})

        # Actualizar datos básicos
        usuario.nombre = nombre
        usuario.email = email
        usuario.fechanacimiento = fechanacimiento or None

        # Si se intentó cambiar la contraseña (al menos uno de los campos no vacío)
        if actual or nueva or confirmar:
            # Validaciones de formulario
            if not actual or not nueva or not confirmar:
                messages.error(request, "Para cambiar la contraseña debes completar los tres campos.")
                return render(request, 'usuario_perfil.html', {'usuario': usuario})
            if nueva != confirmar:
                messages.error(request, "La nueva contraseña y su confirmación no coinciden.")
                return render(request, 'usuario_perfil.html', {'usuario': usuario})

            # Verificar contraseña actual.
            # check_password funciona si la contraseña en DB está hasheada.
            # Si por alguna razón la contraseña almacenada es texto plano,
            # hacemos un fallback que compara directamente (para permitir el cambio).
            try:
                es_correcta = check_password(actual, usuario.contraseña or '')
            except Exception:
                # fallback seguro: comparar texto plano (por compatibilidad con DB antigua)
                es_correcta = (usuario.contraseña == actual)

            if not es_correcta:
                messages.error(request, "La contraseña actual es incorrecta.")
                return render(request, 'usuario_perfil.html', {'usuario': usuario})

            # Asignar nuevo hash y guardar
            usuario.contraseña = make_password(nueva)
            messages.success(request, "Contraseña cambiada correctamente.")

        # Guardar cambios (nombre, email, fecha y posible contraseña)
        try:
            usuario.save()
            messages.success(request, "Datos actualizados correctamente.")
        except Exception as e:
            messages.error(request, f"No se pudieron guardar los cambios: {str(e)}")
            # opcional: rollback o log

        return redirect('perfil_usuario')

    # GET
    # Obtener presentaciones guardadas por el usuario
    guardados = Guardado.objects.filter(idusuario=usuario).select_related(
        'idpresentacion',
        'idpresentacion__idmedicamento',
    ).order_by('-fechaagregado')

    return render(request, 'usuario_perfil.html', {
        'usuario': usuario,
        'guardados': guardados,
    })
# ----------------------------------------------------------









# ------------------------ GRAFICOS DE PRUEBA
from django.shortcuts import render
from django.db.models import Count
from datetime import date
from .models import Usuario
import json

def admin_usuario_graficos(request):
    usuarios = Usuario.objects.all()

    # -------------------- Edad de los usuarios --------------------
    edad_dict = {}
    today = date.today()
    for u in usuarios:
        if u.fechanacimiento:
            edad = today.year - u.fechanacimiento.year
            edad_dict[edad] = edad_dict.get(edad, 0) + 1

    # Ordenar edades ascendente
    edad_labels = sorted(edad_dict.keys())
    edad_values = [edad_dict[edad] for edad in edad_labels]

    # -------------------- Registro por fecha --------------------
    registro_dict = {}
    for u in usuarios:
        fecha = u.fecharegistro.strftime('%Y-%m-%d')
        registro_dict[fecha] = registro_dict.get(fecha, 0) + 1

    # Ordenar por fecha cronológicamente
    registro_labels = sorted(registro_dict.keys())
    registro_values = [registro_dict[fecha] for fecha in registro_labels]

    # -------------------- Usuarios por comuna --------------------
    comuna_dict = usuarios.values('idcomuna__nombrecomuna').annotate(count=Count('idusuario'))
    # Ordenar por cantidad descendente
    comuna_sorted = sorted(comuna_dict, key=lambda x: x['count'], reverse=True)
    comuna_labels = [c['idcomuna__nombrecomuna'] if c['idcomuna__nombrecomuna'] else 'Sin comuna' for c in comuna_sorted]
    comuna_values = [c['count'] for c in comuna_sorted]

    # -------------------- Contexto para la plantilla --------------------
    context = {
        'edadData': json.dumps({'labels': edad_labels, 'data': edad_values}),
        'registroData': json.dumps({'labels': registro_labels, 'data': registro_values}),
        'comunaData': json.dumps({'labels': comuna_labels, 'data': comuna_values}),
    }

    return render(request, 'admin_usuario_graficos.html', context)
