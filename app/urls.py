from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Para el login


urlpatterns = [
    path('', views.index, name='index'), # 4 crear ruta
]