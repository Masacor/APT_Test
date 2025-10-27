from django.db import models
from datetime import date # Para el modelo de usuario - fechas de registro y fecha de nacimiento
from django.contrib.auth.hashers import make_password

# Create your models here.
# -----------------------
# class Presentacion(models.Model):
#     idpresentacion = models.AutoField(primary_key=True)
#     idmedicamento = models.IntegerField()
#     cantidadvalor = models.IntegerField()
#     cantidadunidad = models.CharField(max_length=50)
#     descripcion = models.CharField(max_length=255)

#     class Meta:
#         db_table = 'presentacion'  # Nombre exacto de la tabla en PostgreSQL

class Presentacion(models.Model):
    idpresentacion = models.AutoField(primary_key=True)
    idmedicamento = models.ForeignKey(
        'Medicamento',
        on_delete=models.DO_NOTHING,  # coincide con tu DB
        db_column='idmedicamento',
        blank=True,
        null=True
    )
    cantidadvalor = models.IntegerField()
    cantidadunidad = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)

    class Meta:
        db_table = 'presentacion'
        managed = False


# -----------------------
class PrecioFarmacia(models.Model):
    idprecio = models.AutoField(primary_key=True)
    
    # Relación con Presentacion
    idpresentacion = models.ForeignKey(
        'Presentacion',
        on_delete=models.DO_NOTHING,
        db_column='idpresentacion'
    )
    
    # Relación con Farmacia
    idfarmacia = models.ForeignKey(
        'Farmacia',
        on_delete=models.DO_NOTHING,
        db_column='idfarmacia'
    )

    precio = models.DecimalField(max_digits=10, decimal_places=2)
    preciooferta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecharegistro = models.DateField(default=date.today)
    presentacionurl = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'preciofarmacia'
        managed = False    

    def __str__(self):
        return f"{self.idprecio} - {self.idpresentacion_id} - {self.idfarmacia.nombrefarmacia}"

# -----------------------
class Farmacia(models.Model):
    idfarmacia = models.AutoField(primary_key=True)
    nombrefarmacia = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'farmacia'
        managed = False  # ya existe en PostgreSQL

    def __str__(self):
        return self.nombrefarmacia
    
# -----------------------
class MarcaComercial(models.Model):
    idmarca = models.AutoField(primary_key=True)
    nombremarca = models.CharField(max_length=255)

    class Meta:
        db_table = 'marcacomercial'
        managed = False  # Para no crear la tabla si ya existe

    def __str__(self):
        return self.nombremarca

# -----------------------
class Laboratorio(models.Model):
    idlaboratorio = models.AutoField(primary_key=True)
    nombrelaboratorio = models.CharField(max_length=255)

    class Meta:
        db_table = 'laboratorio'
        managed = False

    def __str__(self):
        return self.nombrelaboratorio

# -----------------------
class Medicamento(models.Model):
    idmedicamento = models.AutoField(primary_key=True)
    registrosanitario = models.CharField(max_length=255, blank=True, null=True)
    
    idlaboratorio = models.ForeignKey(
        Laboratorio, 
        on_delete=models.DO_NOTHING,  # coincide con ON DELETE NO ACTION
        db_column='idlaboratorio', 
        blank=True, 
        null=True
    )
    
    idmarca = models.ForeignKey(
        MarcaComercial, 
        on_delete=models.DO_NOTHING, 
        db_column='idmarca', 
        blank=True, 
        null=True
    )

    class Meta:
        db_table = 'medicamento'
        managed = False

    def __str__(self):
        return f"Medicamento {self.idmedicamento}"

# -----------------------



# -----------------------
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

    # Agregando la columna para admin
    is_admin = models.BooleanField(default=False)  # Nuevo campo para admin

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return self.nombre