import requests
from icalendar import Calendar
from horarios.models import BloqueHorario, PerfilUsuario
from django.contrib.auth.models import User
import pytz
from datetime import datetime, time

def sincronizar_desde_url(url, nombre_usuario):
    usuario, creado = User.objects.get_or_create(username=nombre_usuario)
    BloqueHorario.objects.filter(usuario=usuario).delete()

    # Guardamos la URL en el perfil para futuras sincronizaciones
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario)
    perfil.url_ics = url
    perfil.save()

    _importar_ics(url, usuario)

def resincronizar_usuario(usuario):
    """Re-sincroniza usando la URL guardada"""
    try:
        perfil = PerfilUsuario.objects.get(usuario=usuario)
        if perfil.url_ics:
            BloqueHorario.objects.filter(usuario=usuario).delete()
            _importar_ics(perfil.url_ics, usuario)
            return True
    except PerfilUsuario.DoesNotExist:
        pass
    return False

def _importar_ics(url, usuario):
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    calendario = Calendar.from_ical(respuesta.content)

    tz_chile = pytz.timezone('America/Santiago')

    for componente in calendario.walk('vevent'):
        ramo_original = str(componente.get('summary', ''))
        descripcion = str(componente.get('description', ''))
        texto_busqueda = (ramo_original + " " + descripcion).lower()

<<<<<<< HEAD
        palabras_clave = ["catedra", "cátedra", "auxiliar", "laboratorio", "lab", "control", "taller"]
        if not any(palabra in texto_busqueda for palabra in palabras_clave):
=======
        # Filtro de cátedras y auxiliares
        if "catedra" not in texto_busqueda and "laboratorio" not in texto_busqueda and "control" not in texto_busqueda and "cátedra" not in texto_busqueda and "auxiliar" not in texto_busqueda and "seminario" not in texto_busqueda and "teórica plenaria" not in texto_busqueda and "ayudantía" not in texto_busqueda and "ejercicio" not in texto_busqueda:
>>>>>>> 0da8832e5f735d60ae9926c277c9c1cb811c0d8f
            continue

        # La sala puede venir en LOCATION o al final del SUMMARY después de \n
        sala = str(componente.get('location', ''))
        if not sala and '\\n' in ramo_original:
            partes = ramo_original.split('\\n')
            ramo_original = partes[0].strip()
            sala = partes[1].strip() if len(partes) > 1 else ''

        dtstart_raw = componente.get('dtstart').dt
        dtend_raw = componente.get('dtend').dt

        if isinstance(dtstart_raw, datetime):
            dtstart_local = dtstart_raw.astimezone(tz_chile)
            dtend_local = dtend_raw.astimezone(tz_chile)
            fecha_evento = dtstart_local.date()
            hora_inicio = dtstart_local.time().replace(tzinfo=None)
            hora_fin = dtend_local.time().replace(tzinfo=None)
        else:
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