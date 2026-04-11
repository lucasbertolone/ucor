from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import BloqueHorario, Grupo
from datetime import datetime
import pytz
from .utils import sincronizar_desde_url
import json

def estado_amigos(request):
    # Primero miramos si viene un código en la URL, si no, usamos la cookie
    codigo = request.GET.get('codigo', '').strip().upper()
    if not codigo:
        codigo = request.COOKIES.get('ucor_grupo', '')

    grupo = None
    error_codigo = None

    if codigo:
        try:
            grupo = Grupo.objects.get(codigo=codigo)
            usuarios = grupo.miembros.all()
        except Grupo.DoesNotExist:
            error_codigo = f"No existe ningún grupo con el código '{codigo}'."
            usuarios = User.objects.none()
            codigo = ''  # Limpiamos para no guardar un código inválido
    else:
        usuarios = User.objects.none()

    tz = pytz.timezone('America/Santiago')
    ahora = datetime.now(tz)
    fecha_hoy = ahora.date()
    hora_actual = ahora.time()

    clases_actuales = BloqueHorario.objects.filter(
        fecha=fecha_hoy,
        hora_inicio__lte=hora_actual,
        hora_fin__gte=hora_actual,
        usuario__in=usuarios
    )
    usuarios_en_clase_ids = set(clases_actuales.values_list('usuario', flat=True).distinct())

    amigos_libres = []
    amigos_en_casa = []

    for usuario in usuarios.exclude(id__in=usuarios_en_clase_ids):
        clases_hoy = BloqueHorario.objects.filter(
            usuario=usuario,
            fecha=fecha_hoy
        ).order_by('hora_inicio')

        if not clases_hoy.exists():
            amigos_en_casa.append(usuario)
            continue

        primera_clase = clases_hoy.first().hora_inicio
        ultima_clase = clases_hoy.last().hora_fin

        if hora_actual < primera_clase or hora_actual > ultima_clase:
            amigos_en_casa.append(usuario)
        else:
            amigos_libres.append(usuario)

    contexto = {
        'hora_actual': hora_actual.strftime("%H:%M"),
        'clases_actuales': clases_actuales,
        'amigos_libres': amigos_libres,
        'amigos_en_casa': amigos_en_casa,
        'grupo': grupo,
        'codigo': codigo,
        'error_codigo': error_codigo,
    }

    response = render(request, 'estado.html', contexto)

    # Guardamos el código en una cookie si es válido (dura 1 año)
    if codigo and grupo:
        response.set_cookie('ucor_grupo', codigo, max_age=60*60*24*365)
    elif error_codigo:
        # Si el código es inválido, borramos la cookie
        response.delete_cookie('ucor_grupo')

    return response


def crear_grupo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            grupo = Grupo.objects.create(nombre=nombre)
            return redirect(f'https://ucor-production.up.railway.app/grupo-creado/?codigo={grupo.codigo}')
        return render(request, 'crear_grupo.html', {'error': 'Poné un nombre para el grupo.'})
    return render(request, 'crear_grupo.html')


def grupo_creado(request):
    codigo = request.GET.get('codigo', '')
    try:
        grupo = Grupo.objects.get(codigo=codigo)
    except Grupo.DoesNotExist:
        return redirect('/')
    return render(request, 'grupo_creado.html', {'grupo': grupo})


def agregar_horario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        url = request.POST.get('url_horario', '').strip()
        codigo = request.POST.get('codigo_grupo', '').strip().upper()

        try:
            grupo = Grupo.objects.get(codigo=codigo)
        except Grupo.DoesNotExist:
            return render(request, 'agregar.html', {
                'error': f"El código '{codigo}' no existe. Pide el código correcto a quien creó el grupo.",
                'codigo_previo': codigo,
            })

        try:
            sincronizar_desde_url(url, nombre)
            usuario = User.objects.get(username=nombre)
            grupo.miembros.add(usuario)
            response = redirect(f'/?codigo={codigo}')
            return response
        except Exception as e:
            return render(request, 'agregar.html', {
                'error': 'Error al leer el link. Verifica que sea correcto.',
                'codigo_previo': codigo,
            })

    # Si viene de un grupo, prellenamos el código
    codigo_previo = request.GET.get('codigo', '') or request.COOKIES.get('ucor_grupo', '')
    return render(request, 'agregar.html', {'codigo_previo': codigo_previo})


def comparador_horarios(request):
    codigo = request.GET.get('codigo', '').strip().upper()
    if not codigo:
        codigo = request.COOKIES.get('ucor_grupo', '')

    grupo = None

    if codigo:
        try:
            grupo = Grupo.objects.get(codigo=codigo)
            todos_los_usuarios = grupo.miembros.all()
        except Grupo.DoesNotExist:
            todos_los_usuarios = User.objects.none()
    else:
        todos_los_usuarios = User.objects.all()

    amigos_seleccionados = request.GET.getlist('amigos')

    if amigos_seleccionados:
        bloques = BloqueHorario.objects.filter(
            usuario__username__in=amigos_seleccionados,
            usuario__in=todos_los_usuarios
        )
    else:
        bloques = BloqueHorario.objects.filter(usuario__in=todos_los_usuarios)

    paleta_colores = ['#0d6efd', '#198754', '#dc3545', '#ffc107', '#0dcaf0', '#6f42c1']
    color_usuario = {}
    eventos_calendario = []

    for bloque in bloques:
        nombre_amigo = bloque.usuario.username
        if nombre_amigo not in color_usuario:
            color_usuario[nombre_amigo] = paleta_colores[len(color_usuario) % len(paleta_colores)]
        if bloque.fecha:
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
        'eventos_json': json.dumps(eventos_calendario),
        'grupo': grupo,
        'codigo': codigo,
    }
    return render(request, 'comparador.html', contexto)


def cambiar_grupo(request):
    """Borra la cookie del grupo y manda al inicio"""
    response = redirect('/')
    response.delete_cookie('ucor_grupo')
    return response