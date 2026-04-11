from django.db import models
from django.contrib.auth.models import User
import random
import string

def generar_codigo():
    """Genera un código único tipo UCO-4X7K"""
    chars = string.ascii_uppercase + string.digits
    codigo = ''.join(random.choices(chars, k=4))
    return f"UCO-{codigo}"

class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True, default=generar_codigo)
    creado = models.DateTimeField(auto_now_add=True)
    miembros = models.ManyToManyField(User, related_name='grupos', blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

class BloqueHorario(models.Model):
    DIAS_SEMANA = [
        ('MO', 'Lunes'), ('TU', 'Martes'), ('WE', 'Miércoles'),
        ('TH', 'Jueves'), ('FR', 'Viernes'), ('SA', 'Sábado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ramo = models.CharField(max_length=200)
    sala = models.CharField(max_length=100, blank=True, null=True)
    fecha = models.DateField(null=True)
    dia_semana = models.CharField(max_length=2, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.ramo} - {self.usuario.username} ({self.fecha})"