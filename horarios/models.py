from django.db import models
from django.contrib.auth.models import User

class BloqueHorario(models.Model):
    DIAS_SEMANA = [
        ('MO', 'Lunes'), ('TU', 'Martes'), ('WE', 'Miércoles'),
        ('TH', 'Jueves'), ('FR', 'Viernes'), ('SA', 'Sábado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ramo = models.CharField(max_length=200)
    sala = models.CharField(max_length=100, blank=True, null=True)
    
    # Campo esencial para distinguir semanas y evitar el efecto cascada
    fecha = models.DateField(null=True) 

    dia_semana = models.CharField(max_length=2, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.ramo} - {self.usuario.username} ({self.fecha})"