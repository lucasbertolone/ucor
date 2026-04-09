from django.shortcuts import render
from django.contrib.auth.models import User
from .models import BloqueHorario
from datetime import datetime
import pytz
from django.shortcuts import render, redirect 
from .utils import sincronizar_desde_url
import json 

def estado_amigos(request):
    # 1. Obtenemos la fecha y hora actual en Chile
    tz = pytz.timezone('America/Santiago')
    ahora = datetime.now(tz)
    
    # Extraemos la fecha exacta de hoy y la hora
    fecha_hoy = ahora.date()
    hora_actual = ahora.time()

    # 2. ALGORITMO CORREGIDO: Buscar quién está en clase JUSTO HOY y AHORA
    # Agregamos el filtro fecha=fecha_hoy para evitar duplicados de otras semanas
    clases_actuales = BloqueHorario.objects.filter(
        fecha=fecha_hoy,
        hora_inicio__lte=hora_actual,
        hora_fin__gte=hora_actual
    )
    
    # 3. Separamos a los amigos ocupados de los libres
    # Usamos distinct() para asegurar que cada usuario aparezca una sola vez
    usuarios_ocupados_ids = clases_actuales.values_list('usuario', flat=True).distinct()
    amigos_libres = User.objects.exclude(id__in=usuarios_ocupados_ids)

    # 4. Empaquetamos para el template
    contexto = {
        'hora_actual': hora_actual.strftime("%H:%M"),
        'clases_actuales': clases_actuales,
        'amigos_libres': amigos_libres,
    }
    return render(request, 'estado.html', contexto)

def agregar_horario(request):
    # Si el usuario apretó el botón "Enviar" en el formulario:
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        url = request.POST.get('url_horario')
        
        try:
            # Mandamos a llamar al algoritmo
            sincronizar_desde_url(url, nombre)
            # Si todo sale bien, lo redirigimos a la pantalla principal
            return redirect('/')
        except Exception as e:
            # Si el link es inválido, le mostramos un error
            return render(request, 'agregar.html', {'error': "Error al leer el link. Verifica que sea correcto."})

    # Si el usuario recién entra a la página (GET), mostramos el formulario vacío
    return render(request, 'agregar.html')

def comparador_horarios(request):
    todos_los_usuarios = User.objects.all()
    amigos_seleccionados = request.GET.getlist('amigos')
    
    if amigos_seleccionados:
        bloques = BloqueHorario.objects.filter(usuario__username__in=amigos_seleccionados)
    else:
        bloques = BloqueHorario.objects.all()

    paleta_colores = ['#0d6efd', '#198754', '#dc3545', '#ffc107', '#0dcaf0', '#6f42c1']
    color_usuario = {}
    
    eventos_calendario = []
    for bloque in bloques:
        nombre_amigo = bloque.usuario.username
        
        if nombre_amigo not in color_usuario:
            color_usuario[nombre_amigo] = paleta_colores[len(color_usuario) % len(paleta_colores)]

        # Validamos que el bloque tenga fecha antes de procesarlo
        if bloque.fecha:
            # Combinamos fecha y hora en formato ISO: "YYYY-MM-DDTHH:MM:SS"
            inicio_iso = f"{bloque.fecha.isoformat()}T{bloque.hora_inicio.strftime('%H:%M:%S')}"
            fin_iso = f"{bloque.fecha.isoformat()}T{bloque.hora_fin.strftime('%H:%M:%S')}"

            eventos_calendario.append({
                'title': f"{nombre_amigo}: {bloque.ramo}",
                'start': inicio_iso,
                'end': fin_iso,
                'color': color_usuario[nombre_amigo],
                'extendedProps': {
                    'sala': bloque.sala,
                    'usuario': nombre_amigo
                }
            })

    contexto = {
        'usuarios': todos_los_usuarios,
        'seleccionados': amigos_seleccionados,
        'eventos_json': json.dumps(eventos_calendario) 
    }
    return render(request, 'comparador.html', contexto)
    # 1. Obtenemos a todos los usuarios para la lista de selección
    todos_los_usuarios = User.objects.all()
    
    # 2. Vemos qué amigos seleccionaste en el formulario
    amigos_seleccionados = request.GET.getlist('amigos')
    
    # 3. Filtramos los bloques: si elegiste amigos, mostramos esos. Si no, mostramos todos por defecto.
    if amigos_seleccionados:
        bloques = BloqueHorario.objects.filter(usuario__username__in=amigos_seleccionados)
    else:
        bloques = BloqueHorario.objects.all()

    # 4. Traducimos los días de tu base de datos al formato numérico de FullCalendar (0=Domingo, 1=Lunes...)
    mapa_dias = {'SU': 0, 'MO': 1, 'TU': 2, 'WE': 3, 'TH': 4, 'FR': 5, 'SA': 6}
    
    # Paleta de colores para diferenciar a los amigos
    paleta_colores = ['#0d6efd', '#198754', '#dc3545', '#ffc107', '#0dcaf0', '#6f42c1']
    color_usuario = {}
    
    # 5. Armamos la lista de eventos en formato JSON
    eventos_calendario = []
    for bloque in bloques:
        if not bloque.fecha: continue

        # Combinamos fecha y hora para crear un punto exacto en el tiempo
        start_iso = f"{bloque.fecha.isoformat()}T{bloque.hora_inicio.strftime('%H:%M:%S')}"
        end_iso = f"{bloque.fecha.isoformat()}T{bloque.hora_fin.strftime('%H:%M:%S')}"

        eventos_calendario.append({
            'title': f"{bloque.usuario.username}: {bloque.ramo}",
            'start': start_iso, # Usamos 'start' en lugar de 'startTime'
            'end': end_iso,     # Usamos 'end' en lugar de 'endTime'
                'color': color_usuario.get(bloque.usuario.username, '#0d6efd'),
            'description': bloque.sala
        })
        # Asignamos un color a cada usuario (si no tiene, le damos uno de la paleta)
    contexto = {
        'usuarios': todos_los_usuarios,
        'seleccionados': amigos_seleccionados,
        # Convertimos la lista de Python a un string JSON seguro para JavaScript
        'eventos_json': json.dumps(eventos_calendario) 
    }
    return render(request, 'comparador.html', contexto)