from django.db import models

# Create your models here.


class Archivo(models.Model):
    cedula = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_ingreso = models.DateField()
    cargo = models.CharField(max_length=100)
    grado_cargo = models.CharField(max_length=50)
    antiguedad = models.IntegerField()
    salario = models.DecimalField(max_digits=10, decimal_places=3)