from django.db import models
from datetime import date # Para el modelo de usuario - fechas de registro y fecha de nacimiento
from django.contrib.auth.hashers import make_password

# Create your models here.
class Presentacion(models.Model):
    idpresentacion = models.AutoField(primary_key=True)
    idmedicamento = models.IntegerField()
    cantidadvalor = models.IntegerField()
    cantidadunidad = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)

    class Meta:
        db_table = 'presentacion'  # Nombre exacto de la tabla en PostgreSQL


class Usuario(models.Model):
    idusuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=255, blank=True, null=True)
    proveedoroauth = models.CharField(max_length=255, blank=True, null=True)
    idproveedor = models.CharField(max_length=255, blank=True, null=True)
    idcomuna = models.IntegerField(blank=True, null=True)
    fecharegistro = models.DateField(default=date.today)  # se rellena automáticamente
    fechanacimiento = models.DateField(blank=True, null=True)

    is_admin = models.BooleanField(default=False)  # 👈 Nuevo campo para admin

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return self.nombre