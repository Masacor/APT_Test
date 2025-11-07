from django.urls import path
from . import views

urlpatterns = [
    path('buscadorprueba/', views.index, name='index'),
    path('login/', views.login_usuario, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('', views.landing, name='landing'),
    path('buscador/', views.buscador_prueba, name='buscador_prueba'),
    # urls.py
    path('presentacion/<str:descripcion>/', views.informacion_presentacion, name='informacion_presentacion'),
    # Detalle de presentación (por id)
    path('detalle/<int:id>/', views.detalle_presentacion, name='detalle_presentacion'),
    path('medicamento/<str:descripcion>/', views.informacion_presentacion, name='informacion_presentacion'),




    # ADMIN
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # USUARIO - PROXIMO
    path('dashboard/usuario/', views.admin_usuario, name='admin_usuario'),

    # MEDICAMENTO
    path('dashboard/medicamentos/', views.admin_medicamentos, name='admin_medicamentos'),

    # PRESENTACION
    path('dashboard/presentacion/', views.presentacion, name='presentacion'),

    # LABORATORIO
    path('dashboard/laboratorio/', views.laboratorio, name='laboratorio'),

    # MARCACOMERCIAL
    path('dashboard/marcacomercial/', views.marcacomercial, name='admin_marcacomercial'), 

    # VIAS_ADMINISTRACION
    path('dashboard/vias_administracion/', views.vias_administracion, name='admin_vias_administracion'),

    # FORMAFARMACEUTICA - SE DEBE ARREGLAR PQ NO DEJA ACTUALIZAR EL ELEMENTO, DICE QUE NO SE PUEDE INSERTAR ALGO VACIO
    path('dashboard/formafarmaceutica/', views.formafarmaceutica, name='admin_formafarmaceutica'),

    # PRINCIPIOACTIVO
    path('dashboard/principioactivo/', views.principioactivo, name='admin_principioactivo'),



    # LOS QUE FALTAN
    # MEDICAMENTO_PRINCIPIO
    # path('dashboard/medicamento_principio/', views.medicamento_principio, name='admin_medicamento_principio'),

    # MEDICAMENTO_CATEGORIA
    # path('dashboard/medicamento_categoria/', views.medicamento_categoria, name='admin_medicamento_categoria'),

    # PRECIOFARMACIA
    # path('dashboard/preciofarmacia/', views.preciofarmacia, name='admin_preciofarmacia'),

]