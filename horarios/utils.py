import requests
from icalendar import Calendar
from horarios.models import BloqueHorario
from django.contrib.auth.models import User
import pytz
from datetime import datetime, time

def sincronizar_desde_url(url, nombre_usuario):
    usuario, creado = User.objects.get_or_create(username=nombre_usuario)

    # 1. Borramos el horario anterior
    BloqueHorario.objects.filter(usuario=usuario).delete()

    respuesta = requests.get(url)
    respuesta.raise_for_status()

    calendario = Calendar.from_ical(respuesta.content)
    
    # Definimos la zona horaria local
    tz_chile = pytz.timezone('America/Santiago')

    for componente in calendario.walk('vevent'):
        ramo_original = str(componente.get('summary', ''))
        descripcion = str(componente.get('description', ''))
        texto_busqueda = (ramo_original + " " + descripcion).lower()

        # Filtro de cátedras y auxiliares
        if "catedra" not in texto_busqueda and "laboratorio" not in texto_busqueda and "control" not in texto_busqueda and "cátedra" not in texto_busqueda and "auxiliar" not in texto_busqueda and "seminario" not in texto_busqueda and "teórica plenaria" not in texto_busqueda and "ayudantía" not in texto_busqueda and "ejercicio" not in texto_busqueda:
            continue

        sala = str(componente.get('location', ''))
        
        # Extraemos los objetos de tiempo crudos (en UTC)
        dtstart_raw = componente.get('dtstart').dt
        dtend_raw = componente.get('dtend').dt

        # Verificamos si es un objeto datetime (tiene hora) para hacer la conversión
        if isinstance(dtstart_raw, datetime):
            # Convertimos de UTC a la hora local
            dtstart_local = dtstart_raw.astimezone(tz_chile)
            dtend_local = dtend_raw.astimezone(tz_chile)

            fecha_evento = dtstart_local.date()
            hora_inicio = dtstart_local.time()
            hora_fin = dtend_local.time()
        else:
            # Si el evento es de "todo el día" y solo trae fecha, evitamos que el código falle
            fecha_evento = dtstart_raw
            hora_inicio = time(0, 0)
            hora_fin = time(23, 59)

        dias_map = {0: 'MO', 1: 'TU', 2: 'WE', 3: 'TH', 4: 'FR', 5: 'SA', 6: 'SU'}
        dia = dias_map[fecha_evento.weekday()]

        BloqueHorario.objects.create(
            usuario=usuario,
            ramo=ramo_original,
            fecha=fecha_evento,
            dia_semana=dia,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            sala=sala
        )