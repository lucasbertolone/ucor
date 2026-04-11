"""
Comando para cargar datos de prueba en UCor.
Uso: python manage.py cargar_datos_prueba

Esto crea 4 usuarios ficticios con horarios para la semana actual.
Para borrarlo todo y empezar de nuevo, corré:
    python manage.py cargar_datos_prueba --limpiar
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from horarios.models import BloqueHorario
from datetime import date, time, timedelta

def proximo_dia(dia_semana):
    """Devuelve la fecha del próximo día de la semana dado (0=lunes, 6=domingo)"""
    hoy = date.today()
    dias_adelante = (dia_semana - hoy.weekday()) % 7
    return hoy + timedelta(days=dias_adelante)

# 0=lunes, 1=martes, 2=miercoles, 3=jueves, 4=viernes
LUNES    = proximo_dia(0)
MARTES   = proximo_dia(1)
MIERCOLES = proximo_dia(2)
JUEVES   = proximo_dia(3)
VIERNES  = proximo_dia(4)

DATOS = [
    {
        'nombre': 'Lucas',
        'clases': [
            # Lunes
            {'fecha': LUNES,     'ramo': 'Termodinámica',         'sala': 'QO',   'inicio': time(10,15), 'fin': time(11,45)},
            # Martes
            {'fecha': MARTES,    'ramo': 'Modelación Gráfica',    'sala': 'B211', 'inicio': time(8,30),  'fin': time(10,0)},
            {'fecha': MARTES,    'ramo': 'Programación Software',  'sala': 'B105', 'inicio': time(10,15), 'fin': time(11,45)},
            {'fecha': MARTES,    'ramo': 'Matemáticas Discretas',  'sala': 'F21',  'inicio': time(12,0),  'fin': time(13,30)},
            {'fecha': MARTES,    'ramo': 'Taller Inducción',       'sala': 'F12',  'inicio': time(14,30), 'fin': time(16,0)},
            {'fecha': MARTES,    'ramo': 'Termodinámica Auxiliar', 'sala': 'QO',   'inicio': time(18,0),  'fin': time(19,30)},
            # Miércoles
            {'fecha': MIERCOLES, 'ramo': 'Matemáticas Discretas',  'sala': 'F21',  'inicio': time(16,0),  'fin': time(18,0)},
            # Jueves
            {'fecha': JUEVES,    'ramo': 'Modelación Gráfica',    'sala': 'B211', 'inicio': time(8,30),  'fin': time(10,0)},
            {'fecha': JUEVES,    'ramo': 'Termodinámica',         'sala': 'QO',   'inicio': time(10,15), 'fin': time(11,45)},
            {'fecha': JUEVES,    'ramo': 'Matemáticas Discretas',  'sala': 'F21',  'inicio': time(12,0),  'fin': time(13,30)},
            {'fecha': JUEVES,    'ramo': 'Modelación Auxiliar',   'sala': 'F12',  'inicio': time(14,30), 'fin': time(16,0)},
            {'fecha': JUEVES,    'ramo': 'Taller Prog. Competitiva','sala': 'B001', 'inicio': time(16,15), 'fin': time(17,45)},
            {'fecha': JUEVES,    'ramo': 'Taller Prog. Competitiva','sala': 'S03',  'inicio': time(18,0),  'fin': time(19,30)},
            # Viernes
            {'fecha': VIERNES,   'ramo': 'Programación Software Auxiliar','sala': 'B105','inicio': time(14,30),'fin': time(16,0)},
        ]
    },
    {
        'nombre': 'Valentina',
        'clases': [
            {'fecha': LUNES,     'ramo': 'Cálculo II',            'sala': 'A101', 'inicio': time(9,0),   'fin': time(10,30)},
            {'fecha': LUNES,     'ramo': 'Física I',              'sala': 'B202', 'inicio': time(11,0),  'fin': time(12,30)},
            {'fecha': MARTES,    'ramo': 'Álgebra Lineal',        'sala': 'C301', 'inicio': time(14,0),  'fin': time(15,30)},
            {'fecha': MIERCOLES, 'ramo': 'Cálculo II',            'sala': 'A101', 'inicio': time(9,0),   'fin': time(10,30)},
            {'fecha': MIERCOLES, 'ramo': 'Física I Auxiliar',     'sala': 'B202', 'inicio': time(15,0),  'fin': time(16,30)},
            {'fecha': JUEVES,    'ramo': 'Álgebra Lineal',        'sala': 'C301', 'inicio': time(14,0),  'fin': time(15,30)},
            {'fecha': VIERNES,   'ramo': 'Física I',              'sala': 'B202', 'inicio': time(10,0),  'fin': time(11,30)},
        ]
    },
    {
        'nombre': 'Matias',
        'clases': [
            # Solo tiene clases martes y jueves tarde → libre el resto
            {'fecha': MARTES,    'ramo': 'Introducción a la Programación','sala': 'LAB1','inicio': time(15,0),'fin': time(17,0)},
            {'fecha': JUEVES,    'ramo': 'Introducción a la Programación','sala': 'LAB1','inicio': time(15,0),'fin': time(17,0)},
            {'fecha': JUEVES,    'ramo': 'Estadística',            'sala': 'D401', 'inicio': time(17,30), 'fin': time(19,0)},
        ]
    },
    {
        'nombre': 'Camila',
        'clases': [
            # Tiene clases toda la semana bien distribuidas
            {'fecha': LUNES,     'ramo': 'Literatura',            'sala': 'E501', 'inicio': time(8,0),   'fin': time(9,30)},
            {'fecha': LUNES,     'ramo': 'Historia',              'sala': 'E502', 'inicio': time(10,0),  'fin': time(11,30)},
            {'fecha': MARTES,    'ramo': 'Filosofía',             'sala': 'E503', 'inicio': time(13,0),  'fin': time(14,30)},
            {'fecha': MIERCOLES, 'ramo': 'Literatura',            'sala': 'E501', 'inicio': time(8,0),   'fin': time(9,30)},
            {'fecha': MIERCOLES, 'ramo': 'Taller de Escritura',   'sala': 'E504', 'inicio': time(11,0),  'fin': time(13,0)},
            {'fecha': JUEVES,    'ramo': 'Historia',              'sala': 'E502', 'inicio': time(10,0),  'fin': time(11,30)},
            {'fecha': VIERNES,   'ramo': 'Filosofía',             'sala': 'E503', 'inicio': time(9,0),   'fin': time(10,30)},
        ]
    },
]

class Command(BaseCommand):
    help = 'Carga datos de prueba para UCor'

    def add_arguments(self, parser):
        parser.add_argument('--limpiar', action='store_true', help='Borra todos los datos de prueba')

    def handle(self, *args, **options):
        nombres = [d['nombre'] for d in DATOS]

        if options['limpiar']:
            User.objects.filter(username__in=nombres).delete()
            self.stdout.write(self.style.SUCCESS('✅ Datos de prueba eliminados.'))
            return

        for datos in DATOS:
            usuario, creado = User.objects.get_or_create(username=datos['nombre'])
            BloqueHorario.objects.filter(usuario=usuario).delete()

            for clase in datos['clases']:
                dia_map = {0:'MO', 1:'TU', 2:'WE', 3:'TH', 4:'FR', 5:'SA', 6:'SU'}
                BloqueHorario.objects.create(
                    usuario=usuario,
                    ramo=clase['ramo'],
                    sala=clase['sala'],
                    fecha=clase['fecha'],
                    dia_semana=dia_map[clase['fecha'].weekday()],
                    hora_inicio=clase['inicio'],
                    hora_fin=clase['fin'],
                )

            accion = 'creado' if creado else 'actualizado'
            self.stdout.write(f"  👤 {datos['nombre']} {accion} con {len(datos['clases'])} clases")

        self.stdout.write(self.style.SUCCESS('\n✅ Datos de prueba cargados exitosamente.'))
        self.stdout.write('   Usuarios: ' + ', '.join(nombres))
        self.stdout.write('   Para borrarlos: python manage.py cargar_datos_prueba --limpiar')