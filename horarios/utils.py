import requests
from icalendar import Calendar
from horarios.models import BloqueHorario
from django.contrib.auth.models import User

def sincronizar_desde_url(url, nombre_usuario):
    # 1. Buscamos al usuario, y si no existe, lo creamos mágicamente
    usuario, creado = User.objects.get_or_create(username=nombre_usuario)

    # Borramos sus clases viejas por si está actualizando un horario anterior
    BloqueHorario.objects.filter(usuario=usuario).delete()

    # 2. Descargamos el archivo desde la URL de la universidad
    respuesta = requests.get(url)
    respuesta.raise_for_status() # Esto avisa si el link está roto

    # 3. Leemos el texto descargado como un calendario
    calendario = Calendar.from_ical(respuesta.content)

    # 4. Iteramos por cada evento igual que antes
    for componente in calendario.walk('vevent'):
        ramo = componente.get('summary')
        sala = componente.get('location')
        
        hora_inicio = componente.get('dtstart').dt.time()
        hora_fin = componente.get('dtend').dt.time()

        rrule = componente.get('rrule')
        if rrule and 'BYDAY' in rrule:
            dia = rrule['BYDAY'][0][:2] 
        else:
            dia = 'MO' 

        # Guardamos en la base de datos
        BloqueHorario.objects.create(
            usuario=usuario, ramo=ramo, sala=sala,
            dia_semana=dia, hora_inicio=hora_inicio, hora_fin=hora_fin
        )