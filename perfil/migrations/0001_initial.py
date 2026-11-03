import django.db.models.deletion
import perfil.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracionSitio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(default='MathMaster', max_length=60)),
                ('lema', models.CharField(default='Matemáticas remediales con práctica adaptativa.', max_length=160)),
                ('autor', models.CharField(default='Rubén Andrés Gómez Molina', max_length=100)),
                ('whatsapp', models.CharField(blank=True, default='524661074921', help_text='Solo dígitos con lada de país, sin + ni espacios. Ej: 524661074921', max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
            ],
            options={'verbose_name': 'Configuración del sitio', 'verbose_name_plural': 'Configuración del sitio'},
        ),
        migrations.CreateModel(
            name='RedSocial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=40)),
                ('url', models.CharField(help_text='https://… o mailto:…', max_length=300)),
                ('icono', models.CharField(choices=[('fab fa-github', 'GitHub'), ('fab fa-linkedin', 'LinkedIn'), ('fab fa-whatsapp', 'WhatsApp'), ('fab fa-x-twitter', 'X / Twitter'), ('fab fa-instagram', 'Instagram'), ('fab fa-facebook', 'Facebook'), ('fab fa-youtube', 'YouTube'), ('fab fa-tiktok', 'TikTok'), ('fas fa-envelope', 'Correo'), ('fas fa-globe', 'Sitio web')], default='fas fa-globe', max_length=40)),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('activa', models.BooleanField(default=True)),
            ],
            options={'verbose_name': 'Red social', 'verbose_name_plural': 'Redes sociales', 'ordering': ['orden', 'id']},
        ),
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, upload_to=perfil.models.ruta_avatar)),
                ('bio', models.CharField(blank=True, max_length=280)),
                ('carrera', models.CharField(blank=True, max_length=100)),
                ('semestre', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='perfil', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Perfil', 'verbose_name_plural': 'Perfiles'},
        ),
    ]
