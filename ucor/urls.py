from django.contrib import admin
from django.urls import path
from horarios.views import estado_amigos, agregar_horario, comparador_horarios # Importa la nueva vista

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', estado_amigos), 
    path('agregar/', agregar_horario), 
    path('comparador/', comparador_horarios),
]