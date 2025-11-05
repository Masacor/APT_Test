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
# class Medicamento(models.Model):
#     idmedicamento = models.AutoField(primary_key=True)
#     registrosanitario = models.CharField(max_length=255, blank=True, null=True)
    
#     idlaboratorio = models.ForeignKey(
#         Laboratorio, 
#         on_delete=models.DO_NOTHING,  # coincide con ON DELETE NO ACTION
#         db_column='idlaboratorio', 
#         blank=True, 
#         null=True
#     )
    
#     idmarca = models.ForeignKey(
#         MarcaComercial, 
#         on_delete=models.DO_NOTHING, 
#         db_column='idmarca', 
#         blank=True, 
#         null=True
#     )

#     class Meta:
#         db_table = 'medicamento'
#         managed = False

#     def __str__(self):
#         return f"Medicamento {self.idmedicamento}"

class Medicamento(models.Model):
    idmedicamento = models.AutoField(primary_key=True)
    registrosanitario = models.CharField(max_length=255, blank=True, null=True)

    idlaboratorio = models.ForeignKey(
        'Laboratorio',
        on_delete=models.DO_NOTHING,
        db_column='idlaboratorio',
        blank=True,
        null=True
    )

    idmarca = models.ForeignKey(
        'MarcaComercial',
        on_delete=models.DO_NOTHING,
        db_column='idmarca',
        blank=True,
        null=True
    )

    # 🔄 Estos dos campos solo si existen en la tabla "medicamento" en PostgreSQL:
    idforma = models.ForeignKey(
        'FormaFarmaceutica',
        on_delete=models.DO_NOTHING,
        db_column='idforma',
        blank=True,
        null=True
    )

    id_via = models.ForeignKey(
        'ViasAdministracion',
        on_delete=models.DO_NOTHING,
        db_column='id_via',
        blank=True,
        null=True
    )

    # 🆕 Nueva columna reflejada desde PostgreSQL
    url_foto = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'medicamento'
        managed = False  # evita que Django intente crearla

    def __str__(self):
        return f"Medicamento {self.idmedicamento}"


# ----------------------- Subir todos los faltantes.
# -----------------------
class Region(models.Model):
    idregion = models.AutoField(primary_key=True)
    nombreregion = models.CharField(max_length=255)

    class Meta:
        db_table = 'region'
        managed = False

    def __str__(self):
        return self.nombreregion


# -----------------------
class Comuna(models.Model):
    idcomuna = models.AutoField(primary_key=True)
    idregion = models.ForeignKey(
        Region,
        on_delete=models.DO_NOTHING,
        db_column='idregion',
        blank=True,
        null=True
    )
    nombrecomuna = models.CharField(max_length=255)

    class Meta:
        db_table = 'comuna'
        managed = False

    def __str__(self):
        return self.nombrecomuna


# -----------------------
class Categoria(models.Model):
    idcategoria = models.AutoField(primary_key=True)
    nombrecategoria = models.CharField(max_length=255)

    class Meta:
        db_table = 'categoria'
        managed = False

    def __str__(self):
        return self.nombrecategoria


# -----------------------
class PrincipioActivo(models.Model):
    idprincipio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    class Meta:
        db_table = 'principioactivo'
        managed = False

    def __str__(self):
        return self.nombre


# -----------------------
class FormaFarmaceutica(models.Model):
    idforma = models.AutoField(primary_key=True)
    nombreforma = models.CharField(max_length=255)

    class Meta:
        db_table = 'formafarmaceutica'
        managed = False

    def __str__(self):
        return self.nombreforma


# -----------------------
class ViasAdministracion(models.Model):
    id_via = models.AutoField(primary_key=True)
    via = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'vias_administracion'
        managed = False

    def __str__(self):
        return self.via


# -----------------------
class Guardado(models.Model):
    idguardado = models.AutoField(primary_key=True)

    idusuario = models.ForeignKey(
        'Usuario',
        on_delete=models.DO_NOTHING,
        db_column='idusuario',
        blank=True,
        null=True
    )

    idpresentacion = models.ForeignKey(
        'Presentacion',
        on_delete=models.DO_NOTHING,
        db_column='idpresentacion',
        blank=True,
        null=True
    )

    fechaagregado = models.DateField()

    class Meta:
        db_table = 'guardado'
        managed = False

    def __str__(self):
        return f"Guardado {self.idguardado}"


# -----------------------
class AlertaPrecio(models.Model):
    idalerta = models.AutoField(primary_key=True)

    idguardado = models.ForeignKey(
        Guardado,
        on_delete=models.DO_NOTHING,
        db_column='idguardado',
        blank=True,
        null=True
    )

    precioobjetivo = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    fechaalerta = models.DateField()

    class Meta:
        db_table = 'alertaprecio'
        managed = False

    def __str__(self):
        return f"Alerta {self.idalerta} - Activa: {self.activo}"


# -----------------------
class MedicamentoCategoria(models.Model):
    idmedicamento = models.ForeignKey(
        'Medicamento',
        on_delete=models.DO_NOTHING,
        db_column='idmedicamento'
    )
    idcategoria = models.ForeignKey(
        Categoria,
        on_delete=models.DO_NOTHING,
        db_column='idcategoria'
    )

    class Meta:
        db_table = 'medicamento_categoria'
        managed = False
        unique_together = (('idmedicamento', 'idcategoria'),)

    def __str__(self):
        return f"{self.idmedicamento_id} - {self.idcategoria_id}"


# -----------------------
class MedicamentoPrincipio(models.Model):
    idmedicamento = models.ForeignKey(
        'Medicamento',
        on_delete=models.DO_NOTHING,
        db_column='idmedicamento'
    )
    idprincipio = models.ForeignKey(
        PrincipioActivo,
        on_delete=models.DO_NOTHING,
        db_column='idprincipio'
    )
    concentracionactivo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'medicamento_principio'
        managed = False
        unique_together = (('idmedicamento', 'idprincipio'),)

    def __str__(self):
        return f"{self.idmedicamento_id} - {self.idprincipio_id}"





# -----------------------
# class Usuario(models.Model):
#     idusuario = models.AutoField(primary_key=True)
#     nombre = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     contraseña = models.CharField(max_length=255, blank=True, null=True)
#     proveedoroauth = models.CharField(max_length=255, blank=True, null=True)
#     idproveedor = models.CharField(max_length=255, blank=True, null=True)
#     idcomuna = models.IntegerField(blank=True, null=True)
#     fecharegistro = models.DateField(default=date.today)  # se rellena automáticamente
#     fechanacimiento = models.DateField(blank=True, null=True)

#     # Agregando la columna para admin
#     is_admin = models.BooleanField(default=False)  # Nuevo campo para admin

#     class Meta:
#         db_table = 'usuario'

#     def __str__(self):
#         return self.nombre

class Usuario(models.Model):
    idusuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=255, blank=True, null=True)
    proveedoroauth = models.CharField(max_length=255, blank=True, null=True)
    idproveedor = models.CharField(max_length=255, blank=True, null=True)

    # 🔄 Cambio importante: ahora es una ForeignKey
    idcomuna = models.ForeignKey(
        'Comuna',
        on_delete=models.DO_NOTHING,
        db_column='idcomuna',
        blank=True,
        null=True
    )

    fecharegistro = models.DateField(default=date.today)
    fechanacimiento = models.DateField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = 'usuario'
        managed = False  # importante para no recrear la tabla

    def __str__(self):
        return self.nombre
