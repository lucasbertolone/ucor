from django.db import migrations, models
import horarios.models

class Migration(migrations.Migration):

    dependencies = [
        ('horarios', '0002_bloquehorario_fecha'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('codigo', models.CharField(default=horarios.models.generar_codigo, max_length=10, unique=True)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('miembros', models.ManyToManyField(blank=True, related_name='grupos', to='auth.user')),
            ],
        ),
    ]