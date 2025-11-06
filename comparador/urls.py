from django.urls import path
from . import views

urlpatterns = [
    path('buscador/', views.index, name='index'),
    path('login/', views.login_usuario, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('', views.landing, name='landing'),
    path('buscadorprueba/', views.buscador_prueba, name='buscador_prueba'),
    # urls.py
    path('presentacion/<str:descripcion>/', views.informacion_presentacion, name='informacion_presentacion'),



    # ADMIN
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # USUARIO
    #path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # MEDICAMENTO
    path('dashboard/medicamentos/', views.admin_medicamentos, name='admin_medicamentos'),

    # PRESENTACION
    path('dashboard/presentacion/', views.presentacion, name='presentacion'),

]