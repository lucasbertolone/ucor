from django.contrib import admin
from django.urls import path
from horarios.views import estado_amigos, agregar_horario, comparador_horarios, crear_grupo, grupo_creado, cambiar_grupo, resincronizar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', estado_amigos),
    path('agregar/', agregar_horario),
    path('comparador/', comparador_horarios),
    path('crear-grupo/', crear_grupo),
    path('grupo-creado/', grupo_creado),
    path('cambiar-grupo/', cambiar_grupo),
    path('actualizar/', resincronizar),
]