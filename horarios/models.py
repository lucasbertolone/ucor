from django.db import models
from django.contrib.auth.models import User

class BloqueHorario(models.Model):
    # Definimos las opciones para los días usando el formato que leen los archivos .ics
    DIAS_SEMANA = [
        ('MO', 'Lunes'),
        ('TU', 'Martes'),
        ('WE', 'Miércoles'),
        ('TH', 'Jueves'),
        ('FR', 'Viernes'),
        ('SA', 'Sábado'),
    ]

    # Vinculamos este bloque a un usuario específico
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Datos de la clase
    ramo = models.CharField(max_length=200)
    sala = models.CharField(max_length=100, blank=True, null=True)
    
    # Cuándo ocurre
    dia_semana = models.CharField(max_length=2, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    # Esto es solo para que se lea bonito en el panel de administrador
    def __str__(self):
        return f"{self.ramo} - {self.usuario.username} ({self.dia_semana})"